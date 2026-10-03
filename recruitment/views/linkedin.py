import json
import logging
import os

import requests
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

logger = logging.getLogger(__name__)

from bs4 import BeautifulSoup
from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext_lazy as _

from fits_views.cbv_methods import login_required, permission_required
from recruitment.models import LinkedInAccount


@login_required
@permission_required("recruitment.update_linkedinaccount")
def update_isactive_linkedin(request, obj_id):
    """
    htmx function to update is active field in LinkedInAccount.
    Args:
    - is_active: Boolean value representing the state of LinkedInAccount,
    - obj_id: Id of LinkedInAccount object.
    """
    is_active = request.POST.get("is_active")
    linkedin_account = LinkedInAccount.objects.get(id=obj_id)
    if is_active == "on":
        linkedin_account.is_active = True
        messages.success(request, _("LinkedIn Account activated successfully."))
    else:
        linkedin_account.is_active = False
        messages.success(request, _("LinkedIn Account deactivated successfully."))
    linkedin_account.save()

    return HttpResponse("<script>$('#reloadMessagesButton').click();</script>")


@login_required
@permission_required("recruitment.delete_linkedinaccount")
def delete_linkedin_account(request, pk, return_redirect=True):
    """
    Delete Linkedin account
    """
    try:
        if return_redirect:
            LinkedInAccount.objects.get(id=pk).delete()
            messages.success(request, "Linkedin data deleted")
            return redirect(reverse("linkedin-setting-list"))
    except Exception as e:
        logger(e)
        messages.error(request, "Something went wrong")


@login_required
def check_linkedin(request):
    import requests as _req

    token_resp = _req.post(
        "https://www.linkedin.com/oauth/v2/accessToken",
        data={
            "grant_type": "authorization_code",
            "code": os.environ.get("LINKEDIN_AUTH_CODE", ""),
            "redirect_uri": os.environ.get(
                "LINKEDIN_REDIRECT_URI",
                "https://www.linkedin.com/developers/tools/oauth/redirect",
            ),
            "client_id": os.environ.get("LINKEDIN_CLIENT_ID", ""),
            "client_secret": os.environ.get("LINKEDIN_CLIENT_SECRET", ""),
        },
    )
    token_data = token_resp.json()

    if "access_token" not in token_data:
        return JsonResponse({"error": "Token exchange failed", "detail": token_data}, status=400)

    access_token = token_data["access_token"]
    userinfo = _req.get(
        "https://api.linkedin.com/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
    ).json()

    return JsonResponse({
        "access_token": access_token,
        "sub": userinfo.get("sub", ""),
        "email": userinfo.get("email", ""),
        "name": userinfo.get("name", ""),
        "note": "Copy 'access_token' and 'sub' — enter them in LinkedIn Settings to create a LinkedInAccount.",
    })


def linkedin_oauth_start(request):
    """Redirect user to LinkedIn OAuth to get openid + w_member_social token."""
    import urllib.parse

    client_id = os.environ.get("LINKEDIN_CLIENT_ID", "")
    redirect_uri = os.environ.get(
        "LINKEDIN_REDIRECT_URI", "https://hcmspro.net/recruitment/linkedin/callback/"
    )
    scope = "w_member_social r_profile_basicinfo"
    state = "hcms-linkedin-connect"

    params = urllib.parse.urlencode({
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "state": state,
    })
    return redirect(f"https://www.linkedin.com/oauth/v2/authorization?{params}")


def linkedin_oauth_callback(request):
    """Handle LinkedIn OAuth callback, exchange code for token, create LinkedInAccount."""
    import requests as _req
    from base.models import Company

    def _html_card(title, icon, heading, body_html, is_error=False):
        border = "#ef4444" if is_error else "#22c55e"
        return HttpResponse(f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>{title}</title><style>
body{{font-family:sans-serif;display:flex;align-items:center;justify-content:center;
min-height:100vh;margin:0;background:#f4f6f8}}
.card{{background:white;border-radius:12px;padding:40px 48px;
box-shadow:0 4px 24px rgba(0,0,0,.1);text-align:center;max-width:460px;
border-top:4px solid {border}}}
.icon{{font-size:48px;margin-bottom:16px}}
h2{{margin:0 0 12px;color:#1a1a2e}}
p{{color:#555;margin:0 0 12px;font-size:14px;line-height:1.6}}
code{{display:inline-block;background:#f0f4f8;border-radius:6px;
padding:6px 14px;font-size:13px;color:#1a1a2e;margin:4px 0}}
.note{{font-size:12px;color:#999;margin-top:20px}}
</style></head><body><div class="card">
<div class="icon">{icon}</div><h2>{heading}</h2>{body_html}
</div></body></html>""")

    error = request.GET.get("error")
    if error:
        desc = request.GET.get("error_description", error)
        return _html_card(
            "LinkedIn Error", "❌", "LinkedIn Authorization Failed",
            f"<p>{desc}</p><p>Close this tab and try connecting again from HCMS.</p>",
            is_error=True,
        )

    code = request.GET.get("code")
    if not code:
        return _html_card(
            "LinkedIn Error", "❌", "No Authorization Code",
            "<p>LinkedIn did not return an authorization code.</p>"
            "<p>Close this tab and try again from HCMS.</p>",
            is_error=True,
        )

    redirect_uri = os.environ.get(
        "LINKEDIN_REDIRECT_URI", "https://hcmspro.net/recruitment/linkedin/callback/"
    )
    client_id = os.environ.get("LINKEDIN_CLIENT_ID", "")
    client_secret = os.environ.get("LINKEDIN_CLIENT_SECRET", "")

    token_resp = _req.post(
        "https://www.linkedin.com/oauth/v2/accessToken",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "client_secret": client_secret,
        },
        timeout=15,
    )
    token_data = token_resp.json()

    if "access_token" not in token_data:
        return _html_card(
            "LinkedIn Error", "❌", "Token Exchange Failed",
            f"<p>{token_data.get('error_description', 'unknown error')}</p>"
            "<p>Close this tab and try again from HCMS.</p>",
            is_error=True,
        )

    access_token = token_data["access_token"]

    profile_resp = _req.get(
        "https://api.linkedin.com/v2/me",
        headers={"Authorization": f"Bearer {access_token}", "X-Restli-Protocol-Version": "2.0.0"},
        timeout=10,
    ).json()
    sub = str(profile_resp.get("id", ""))
    name = (profile_resp.get("localizedFirstName", "") + " " + profile_resp.get("localizedLastName", "")).strip()

    profile_resp2 = {}
    if not sub:
        profile_resp2 = _req.get(
            "https://api.linkedin.com/rest/me",
            headers={"Authorization": f"Bearer {access_token}", "LinkedIn-Version": "202306"},
            timeout=10,
        ).json()
        sub = str(profile_resp2.get("id", ""))
        name = (profile_resp2.get("localizedFirstName", "") + " " + profile_resp2.get("localizedLastName", "")).strip()

    email = getattr(request.user, "email", "") or "admin@hcmspro.net"
    name = name or "HCMS LinkedIn Account"

    # Fall back to a stable unique ID derived from the token if profile lookup failed
    if not sub:
        import hashlib
        sub = "hcms-" + hashlib.sha256(access_token.encode()).hexdigest()[:16]

    company = Company.objects.filter(is_active=True).first()
    LinkedInAccount.objects.update_or_create(
        sub_id=sub,
        defaults={
            "username": name,
            "email": email,
            "api_token": access_token,
            "organization_id": "113341432",
            "company_id": company,
        },
    )

    return _html_card(
        "LinkedIn Connected", "&#x2705;", "LinkedIn Connected!",
        "<p>Your LinkedIn account has been saved successfully.</p>"
        "<p><strong>Next:</strong> Return to your HCMS browser tab and go to<br>"
        "<code>Settings &rarr; Recruitment &rarr; LinkedIn Integration</code><br>"
        "to confirm the connection.</p>"
        "<p class='note'>You can safely close this tab.</p>",
    )


@login_required
def validate_linkedin_token(request, pk):
    linkedin_account = LinkedInAccount.objects.filter(id=pk).first()
    access_token = linkedin_account.api_token
    url = "https://api.linkedin.com/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        messages.success(request, _("LinkedIn connection success."))
    else:
        messages.success(request, _("LinkedIn connection failed."))
    return HttpResponse("<script>$('#reloadMessagesButton').click();</script>")


def html_to_text(html):
    soup = BeautifulSoup(html, "html.parser")
    return "\n".join(
        p.get_text(strip=True)
        for p in soup.find_all(["p", "br"])
        if p.get_text(strip=True)
    )


@login_required
def post_recruitment_in_linkedin(
    request, recruitment, linkedin_acc, feed_type="feed", group_id=None, source="linkedin"
):
    site_url = request.build_absolute_uri("/")[:-1]  # Gets the base URL
    recruitment_url = (
        f"{site_url}/recruitment/application-form?recruitmentId={recruitment.id}&source={source}"
    )

    payload_dict = {
        "author": f"urn:li:person:{linkedin_acc.sub_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": html_to_text(recruitment.description)},
                "shareMediaCategory": "ARTICLE",
                "media": [
                    {
                        "status": "READY",
                        "description": {"text": recruitment.description},
                        "originalUrl": recruitment_url,
                        "title": {"text": recruitment.title},
                        "thumbnails": [{"url": recruitment_url}],
                    }
                ],
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": (
                "PUBLIC" if feed_type == "feed" else "CONTAINER"
            )
        },
    }

    if feed_type == "group" and group_id:
        payload_dict["containerEntity"] = f"urn:li:group:{group_id}"

    url = "https://api.linkedin.com/v2/ugcPosts"
    payload = json.dumps(payload_dict)
    headers = {
        "Authorization": f"Bearer {linkedin_acc.api_token}",
        "Content-Type": "application/json",
    }
    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 201:
        response_data = response.json()
        recruitment.linkedin_post_id = response_data.get("id")  # Store post ID
        recruitment.save()
    else:
        recruitment.publish_in_linkedin = False
        recruitment.save()


@login_required
def delete_post(recruitment):
    """Delete recruitment post from LinkedIn"""
    linkedin_post_id = recruitment.linkedin_post_id
    if not linkedin_post_id:
        return True  # 787

    url = f"https://api.linkedin.com/v2/ugcPosts/{linkedin_post_id}"
    headers = {
        "Authorization": f"Bearer {recruitment.linkedin_account_id.api_token}",
        "Content-Type": "application/json",
    }

    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        recruitment.linkedin_post_id = None
        recruitment.save()
        return True

    return False
