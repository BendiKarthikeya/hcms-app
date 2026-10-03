{% load i18n static %}
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{% trans "Careers" %} | {% trans "Fintech" %}</title>
  <link rel="stylesheet" href="{% static 'build/css/style.min.css' %}" />
  <style>
    :root {
      --green-50:  #f0faf0;
      --green-100: #d6f0d6;
      --green-200: #a8dca8;
      --green-400: #4caf50;
      --green-600: #2e7d32;
      --green-700: #1b5e20;
      --white:     #ffffff;
      --gray-50:   #f8faf5;
      --gray-100:  #eef2eb;
      --gray-300:  #c8d5c4;
      --gray-500:  #6b7c6b;
      --gray-700:  #374137;
      --gray-900:  #1a2e1a;
    }
    *, *::before, *::after { box-sizing: border-box; }
    html, body {
      margin: 0;
      min-height: 100%;
      background: var(--gray-50);
      color: var(--gray-900);
      font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    a { color: inherit; text-decoration: none; }

    /* ── PAGE SHELL ── */
    .page-shell {
      max-width: 1200px;
      margin: 0 auto;
      padding: 1.75rem 1.5rem 3rem;
    }

    /* ── HERO ── */
    .hero {
      position: relative;
      overflow: hidden;
      padding: 3rem 2.5rem;
      border-radius: 1.75rem;
      background: var(--white);
      border: 1px solid var(--green-100);
      box-shadow: 0 4px 24px rgba(46,125,50,0.07);
    }
    .hero::before {
      content: "";
      position: absolute;
      top: -60px; right: -80px;
      width: 280px; height: 280px;
      background: rgba(76,175,80,0.10);
      filter: blur(70px);
      border-radius: 999px;
    }
    .hero-content { position: relative; z-index: 1; max-width: 720px; }
    .eyebrow {
      display: inline-flex;
      align-items: center;
      gap: .6rem;
      margin-bottom: 1rem;
      background: var(--green-50);
      color: var(--green-600);
      font-size: .8rem;
      font-weight: 700;
      letter-spacing: .16em;
      text-transform: uppercase;
      padding: .3rem .85rem;
      border-radius: 999px;
      border: 1px solid var(--green-100);
    }
    .hero-title {
      margin: 0;
      font-size: clamp(2.4rem, 4.5vw, 3.8rem);
      line-height: 1.04;
      letter-spacing: -.035em;
      color: var(--green-700);
    }
    .hero-copy {
      margin: 1.4rem 0 0;
      color: var(--gray-500);
      font-size: 1.02rem;
      line-height: 1.85;
    }
    .hero-actions {
      display: flex;
      flex-wrap: wrap;
      gap: .9rem;
      margin-top: 2rem;
    }
    .btn-primary {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: .85rem 1.6rem;
      border-radius: 999px;
      background: var(--green-400);
      color: var(--white);
      font-weight: 700;
      font-size: .95rem;
      border: none;
      cursor: pointer;
      transition: background .18s, transform .18s;
    }
    .btn-primary:hover { background: var(--green-600); transform: translateY(-1px); }
    .btn-secondary {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: .85rem 1.6rem;
      border-radius: 999px;
      background: var(--white);
      color: var(--green-600);
      font-weight: 700;
      font-size: .95rem;
      border: 1px solid var(--green-200);
      cursor: pointer;
      transition: background .18s, border-color .18s;
    }
    .btn-secondary:hover { background: var(--green-50); border-color: var(--green-400); }

    /* ── METRICS ── */
    .metrics {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: .9rem;
      margin-top: 2.2rem;
    }
    .metric-card {
      padding: 1.1rem 1.2rem;
      border-radius: 1.25rem;
      background: var(--green-50);
      border: 1px solid var(--green-100);
    }
    .metric-value {
      margin: 0;
      font-size: 1.85rem;
      font-weight: 800;
      color: var(--green-600);
    }
    .metric-label {
      margin: .45rem 0 0;
      color: var(--gray-500);
      font-size: .9rem;
      line-height: 1.6;
    }

    /* ── SECTION ── */
    .section { margin-top: 2.75rem; }
    .section-header { display: flex; flex-wrap: wrap; align-items: flex-end; justify-content: space-between; gap: 1rem; }
    .section-header h2 { margin: 0; font-size: 1.85rem; color: var(--green-700); }
    .section-subtitle { margin: .65rem 0 0; max-width: 700px; color: var(--gray-500); font-size: .98rem; line-height: 1.8; }

    /* ── VALUE CARDS ── */
    .value-grid {
      display: grid;
      gap: .9rem;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      margin-top: 1.75rem;
    }
    .value-card {
      padding: 1.5rem;
      border-radius: 1.25rem;
      background: var(--white);
      border: 1px solid var(--green-100);
      min-height: 160px;
    }
    .value-card h3 { margin: 0 0 .75rem; color: var(--green-700); font-size: 1.08rem; }
    .value-card p  { margin: 0; color: var(--gray-500); line-height: 1.75; font-size: .95rem; }

    /* ── JOB CARDS ── */
    .jobs-grid {
      display: grid;
      gap: 1.25rem;
      grid-template-columns: repeat(auto-fit, minmax(290px, 1fr));
      margin-top: 1.75rem;
    }
    .job-card {
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 1.1rem;
      padding: 1.6rem;
      border-radius: 1.5rem;
      background: var(--white);
      border: 1px solid var(--green-100);
      box-shadow: 0 2px 12px rgba(46,125,50,0.06);
      transition: transform .15s, border-color .15s, box-shadow .15s;
      min-height: 280px;
    }
    .job-card:hover {
      transform: translateY(-3px);
      border-color: var(--green-400);
      box-shadow: 0 8px 28px rgba(46,125,50,0.12);
    }
    .job-meta {
      display: flex;
      flex-wrap: wrap;
      gap: .6rem;
    }
    /* ── FIX: only show badge pill if it has content ── */
    .job-meta span {
      display: none; /* hidden by default */
      padding: .35rem .75rem;
      border-radius: 999px;
      background: var(--green-50);
      color: var(--green-600);
      font-size: .85rem;
      font-weight: 600;
      border: 1px solid var(--green-100);
    }
    .job-meta span:not(:empty) {
      display: inline-flex; /* only show when there's text */
    }
    .job-title { margin: 0; font-size: 1.25rem; color: var(--green-700); line-height: 1.3; }
    .job-description { margin: 0; color: var(--gray-500); line-height: 1.8; flex: 1; font-size: .93rem; }
    .job-footer {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: .9rem;
    }
    .badge-pill {
      display: inline-flex;
      align-items: center;
      gap: .4rem;
      padding: .55rem .9rem;
      border-radius: 999px;
      background: var(--green-50);
      color: var(--green-600);
      font-size: .9rem;
      font-weight: 700;
      border: 1px solid var(--green-100);
    }
    .apply-link {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: .75rem 1.3rem;
      border-radius: 999px;
      background: var(--green-400);
      color: var(--white);
      font-weight: 700;
      font-size: .92rem;
      border: none;
      cursor: pointer;
      transition: background .15s, transform .15s;
    }
    .apply-link:hover { background: var(--green-600); transform: translateY(-1px); }

    .empty-state {
      padding: 2rem;
      border-radius: 1.25rem;
      background: var(--white);
      border: 1px dashed var(--green-200);
      text-align: center;
      color: var(--gray-500);
      margin-top: 1.25rem;
    }

    /* ── MODAL ── */
    .modal-overlay {
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(27, 94, 32, 0.35);
      z-index: 1000;
      justify-content: center;
      align-items: center;
      padding: 1rem;
    }
    .modal-overlay.active { display: flex; }
    .modal-content {
      background: var(--white);
      border: 1px solid var(--green-100);
      border-radius: 1.5rem;
      width: 100%;
      max-width: 520px;
      max-height: 88vh;           /* ← cap height */
      display: flex;
      flex-direction: column;
      box-shadow: 0 20px 60px rgba(27,94,32,0.18);
      animation: slideIn .25s ease;
      overflow: hidden;           /* clip children */
    }
    @keyframes slideIn {
      from { transform: translateY(-30px); opacity: 0; }
      to   { transform: translateY(0);     opacity: 1; }
    }
    .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1.1rem 1.4rem .9rem;
      border-bottom: 1px solid var(--green-100);
      flex-shrink: 0;
    }
    .modal-header h2 { margin: 0; color: var(--green-700); font-size: 1.15rem; }
    .modal-close {
      background: var(--green-50);
      border: 1px solid var(--green-100);
      color: var(--gray-500);
      cursor: pointer;
      font-size: 1.1rem;
      width: 28px; height: 28px;
      border-radius: 999px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background .15s;
    }
    .modal-close:hover { background: var(--green-100); color: var(--green-700); }

    /* scrollable body */
    .modal-body {
      padding: 1.1rem 1.4rem;
      overflow-y: auto;
      flex: 1;
    }

    .job-desc-body { color:var(--gray-700); line-height:1.8; font-size:.95rem; }
    .job-desc-body h1,.job-desc-body h2,.job-desc-body h3,.job-desc-body h4 { margin:.9rem 0 .4rem; color:var(--gray-900); }
    .job-desc-body p { margin:.5rem 0; }
    .job-desc-body ul,.job-desc-body ol { padding-left:1.4rem; margin:.5rem 0; }
    .job-desc-body li { margin:.2rem 0; }
    .job-desc-body strong { color:var(--gray-900); }

    .form-group { margin-bottom: 1rem; }
    .form-group label {
      display: block;
      color: var(--gray-700);
      font-size: .85rem;
      margin-bottom: .35rem;
      font-weight: 600;
    }
    .form-group input,
    .form-group textarea,
    .form-group select {
      width: 100%;
      padding: .6rem .75rem;
      border: 1px solid var(--green-200);
      border-radius: .65rem;
      background: var(--gray-50);
      color: var(--gray-900);
      font-family: inherit;
      font-size: .9rem;
      transition: border-color .15s, background .15s;
    }
    .form-group input:focus,
    .form-group textarea:focus,
    .form-group select:focus {
      outline: none;
      border-color: var(--green-400);
      background: var(--white);
    }
    /* compact textareas */
    .form-group textarea { rows: 3; resize: vertical; min-height: 72px; }

    .form-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: .85rem;
    }

    .modal-footer {
      display: flex;
      gap: .85rem;
      padding: .9rem 1.4rem 1.1rem;
      border-top: 1px solid var(--green-100);
      flex-shrink: 0;
    }
    .modal-btn {
      flex: 1;
      padding: .75rem;
      border-radius: .65rem;
      border: none;
      cursor: pointer;
      font-weight: 600;
      font-size: .92rem;
      transition: all .18s;
    }
    .modal-btn-submit {
      background: var(--green-400);
      color: var(--white);
    }
    .modal-btn-submit:hover { background: var(--green-600); }
    .modal-btn-cancel {
      background: var(--gray-100);
      color: var(--gray-700);
      border: 1px solid var(--green-100);
    }
    .modal-btn-cancel:hover { background: var(--green-50); }

    .success-message {
      text-align: center;
      padding: 2rem 1.5rem;
      color: var(--gray-500);
    }
    .success-message h3 { color: var(--green-600); margin-bottom: .75rem; font-size: 1.15rem; }

    /* ── RESPONSIVE ── */
    @media (max-width: 640px) {
      .hero { padding: 1.75rem 1.25rem; }
      .hero-title { font-size: 2.1rem; }
      .hero-actions { flex-direction: column; }
      .form-row { grid-template-columns: 1fr; }
      .modal-content { max-height: 92vh; }
    }
  </style>
</head>
<body>
  <div class="page-shell">

    <!-- HERO -->
    <section class="hero">
      <div class="hero-content">
        <div class="eyebrow">{% trans "Fintech Careers" %}</div>
        <h1 class="hero-title">{% trans "Build the future of digital finance with a modern high-growth team." %}</h1>
        <p class="hero-copy">{% trans "Join a fintech company creating product-led payments, risk, and treasury tools for ambitious customers around the world." %}</p>
        <div class="hero-actions">
          <a href="#jobs" class="btn-primary">{% trans "View open roles" %}</a>
          <a href="#jobs" class="btn-secondary" onclick="document.getElementById('jobs').scrollIntoView({behavior:'smooth'}); return false;">{% trans "Browse jobs" %}</a>
        </div>
        <div class="metrics">
          <div class="metric-card">
            <p class="metric-value">100%</p>
            <p class="metric-label">{% trans "Remote friendly" %}</p>
          </div>
          <div class="metric-card">
            <p class="metric-value">30+</p>
            <p class="metric-label">{% trans "Open roles" %}</p>
          </div>
          <div class="metric-card">
            <p class="metric-value">{% trans "Fast" %}</p>
            <p class="metric-label">{% trans "Growth stage" %}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- WHY JOIN US -->
    <section class="section">
      <div class="section-header">
        <div>
          <h2>{% trans "Why join us" %}</h2>
          <p class="section-subtitle">{% trans "We bring together design, engineering, and compliance to build secure finance products people trust." %}</p>
        </div>
      </div>
      <div class="value-grid">
        <article class="value-card">
          <h3>{% trans "High-impact work" %}</h3>
          <p>{% trans "Own features that help companies move money faster and with more confidence." %}</p>
        </article>
        <article class="value-card">
          <h3>{% trans "Modern stack" %}</h3>
          <p>{% trans "Build resilient, cloud-native systems with strong observability and security." %}</p>
        </article>
        <article class="value-card">
          <h3>{% trans "Collaborative culture" %}</h3>
          <p>{% trans "Partner across product, data, and operations to ship polished financial experiences." %}</p>
        </article>
      </div>
    </section>

    <!-- OPEN POSITIONS -->
    <section class="section" id="jobs">
      <div class="section-header">
        <div>
          <h2>{% trans "Open positions" %}</h2>
          <p class="section-subtitle">{% trans "Browse current opportunities and apply directly from the job card." %}</p>
        </div>
      </div>

      {% if recruitments %}
        <div class="jobs-grid">
          {% for rec in recruitments %}
            <article class="job-card" style="cursor:pointer;"
              onclick="openJobDesc(this)"
              data-rec-id="{{ rec.id }}"
              data-rec-title="{{ rec.title|escapejs }}"
              data-rec-company="{{ rec.company_id.company|escapejs }}"
              data-rec-vacancy="{% if rec.vacancy %}{{ rec.vacancy }}{% else %}{{ rec.open_positions.all|length }}{% endif %}"
              data-rec-department="{{ rec.department_id.department|default:''|escapejs }}"
              data-rec-position="{{ rec.job_position_id.job_position|default:''|escapejs }}"
              data-rec-employment="{{ rec.get_employment_type_display|default:''|escapejs }}"
              data-rec-location="{{ rec.location|default:''|escapejs }}"
              data-rec-workmode="{{ rec.band|default:''|escapejs }}"
              data-rec-priority="{{ rec.grade|default:''|escapejs }}"
              data-rec-budget="{% if rec.budget %}${{ rec.budget|floatformat:0 }}{% endif %}">
              <div class="job-desc-html" style="display:none;">{{ rec.description }}</div>
              <div>
                <div class="job-meta">
                  <span>{{ rec.company_id.company }}</span>
                  <span>{{ rec.job_position_id.job_position }}</span>
                  {% if rec.location %}<span>{{ rec.location }}</span>{% endif %}
                  {% if rec.band %}<span>{{ rec.band }}</span>{% endif %}
                </div>
                <h3 class="job-title">{{ rec.title }}</h3>
                <p class="job-description">{{ rec.description|striptags|truncatechars:150 }}</p>
              </div>
              <div class="job-footer">
                <span class="badge-pill">
                  {% if rec.vacancy %}{{ rec.vacancy }}{% else %}{{ rec.open_positions.all|length }}{% endif %}
                  {% trans "positions" %}
                </span>
                <a href="#" onclick="openApplicationModal({{ rec.id }}, '{{ rec.title|escapejs }}'); event.stopPropagation(); return false;" class="apply-link">{% trans "Apply" %}</a>
              </div>
            </article>
          {% endfor %}
        </div>
      {% else %}
        <div class="empty-state">
          <p>{% trans "No open positions are available at the moment. Check back soon for our next fintech roles." %}</p>
        </div>
      {% endif %}
    </section>

  </div><!-- /page-shell -->

  <!-- ── APPLICATION MODAL ── -->
  <div class="modal-overlay" id="applicationModal">
    <div class="modal-content">

      <!-- Header (fixed) -->
      <div class="modal-header">
        <h2 id="modalJobTitle">{% trans "Apply for role" %}</h2>
        <button type="button" class="modal-close" onclick="closeApplicationModal()" aria-label="Close">×</button>
      </div>

      <!-- Scrollable body -->
      <div class="modal-body">
        <form id="careerApplicationForm" method="post" enctype="multipart/form-data">
          {% csrf_token %}
          <input type="hidden" name="recruitment_id" id="applicationRecruitmentId" />

          <div class="form-row">
            <div class="form-group">
              <label for="firstName">{% trans "First name" %}</label>
              <input id="firstName" name="first_name" type="text" placeholder="Jane" required />
            </div>
            <div class="form-group">
              <label for="lastName">{% trans "Last name" %}</label>
              <input id="lastName" name="last_name" type="text" placeholder="Smith" required />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="emailAddress">{% trans "Email" %}</label>
              <input id="emailAddress" name="email" type="email" placeholder="jane@example.com" required />
            </div>
            <div class="form-group">
              <label for="phoneNumber">{% trans "Phone" %}</label>
              <input id="phoneNumber" name="phone" type="tel" placeholder="+1 555 000 0000" required />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="countryField">{% trans "Country" %}</label>
              <input id="countryField" name="country" type="text" required />
            </div>
            <div class="form-group">
              <label for="addressField">{% trans "Address" %}</label>
              <input id="addressField" name="address" type="text" required />
            </div>
          </div>

          <div class="form-group">
            <label for="experienceField">{% trans "Experience summary" %}</label>
            <textarea id="experienceField" name="experience" rows="3" required></textarea>
          </div>

          <div class="form-group">
            <label for="whyApplyField">{% trans "Why are you interested in this role?" %}</label>
            <textarea id="whyApplyField" name="why_apply" rows="3" required></textarea>
          </div>

          <div class="form-group">
            <label for="resumeUpload">{% trans "Upload resume" %} <span style="font-weight:400;color:var(--gray-500)">(PDF, DOC, DOCX) *</span></label>
            <input id="resumeUpload" name="resume" type="file" accept=".pdf,.doc,.docx" required/>
          </div>

          <div class="form-group">

            <label for="coverLetterUpload">{% trans "Cover Letter" %} <span style="font-weight:400;color:var(--gray-500)">(PDF)</span></label>
            <input id="coverLetterUpload" name="cover_letter" type="file" accept=".pdf"/>
          </div>

          <div class="form-group">
            <label for="graduationUpload">{% trans "Graduation Certificate" %} <span style="font-weight:400;color:var(--gray-500)">(PDF)</span></label>
            <input id="graduationUpload" name="graduation_certificate" type="file" accept=".pdf"/>
          </div>

          <div class="form-group">
            <label for="transcriptsUpload">{% trans "Transcripts" %} <span style="font-weight:400;color:var(--gray-500)">(PDF)</span></label>
            <input id="transcriptsUpload" name="transcripts" type="file" accept=".pdf"/>
          </div>
        </form>

        <!-- Success state (hidden until submit) -->
        <div class="success-message" id="applicationSuccessMessage" style="display:none;">
          <h3>{% trans "Application received" %}</h3>
          <p>{% trans "Thanks for applying. We will review your submission and contact you shortly." %}</p>
        </div>
      </div>

      <!-- Footer buttons (fixed) -->
      <div class="modal-footer" id="modalFooter">
        <button type="button" class="modal-btn modal-btn-cancel" onclick="closeApplicationModal()">{% trans "Cancel" %}</button>
        <button type="submit" form="careerApplicationForm" class="modal-btn modal-btn-submit" id="submitBtn">{% trans "Submit application" %}</button>
      </div>

    </div>
  </div>

  <!-- ── JOB DESCRIPTION MODAL ── -->
  <div class="modal-overlay" id="jobDescModal">
    <div class="modal-content" style="max-width:680px;">
      <div class="modal-header">
        <h2 id="jobDescTitle" style="font-size:1.25rem;"></h2>
        <button type="button" class="modal-close" onclick="closeJobDesc()" aria-label="Close">×</button>
      </div>
      <div class="modal-body">
        <div id="jobDescMeta" class="job-meta" style="margin-bottom:1.25rem;"></div>
        <div id="jobDescContent" class="job-desc-body"></div>
      </div>
      <div class="modal-footer">
        <button type="button" class="modal-btn modal-btn-cancel" onclick="closeJobDesc()">{% trans "Close" %}</button>
        <button type="button" class="modal-btn modal-btn-submit" id="jobDescApplyBtn">{% trans "Apply for this role" %}</button>
      </div>
    </div>
  </div>

 <script>
  function scrollToJobs() {
    document.getElementById('jobs').scrollIntoView({ behavior: 'smooth' });
  }

  function openApplicationModal(recruitmentId, jobTitle) {
    document.getElementById('applicationRecruitmentId').value = recruitmentId;
     // ✅ ADD THIS BLOCK HERE
  let existing = document.getElementById("jobTitleHidden");
  if (!existing) {
    let input = document.createElement("input");
    input.type = "hidden";
    input.name = "job_title";
    input.id = "jobTitleHidden";
    document.getElementById("careerApplicationForm").appendChild(input);
  }
  document.getElementById("jobTitleHidden").value = jobTitle;
  // ✅ END
    document.getElementById('modalJobTitle').textContent = jobTitle;
    document.getElementById('applicationSuccessMessage').style.display = 'none';
    document.getElementById('careerApplicationForm').style.display = 'block';
    document.getElementById('modalFooter').style.display = 'flex';
    document.getElementById('applicationModal').classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeApplicationModal() {
    document.getElementById('applicationModal').classList.remove('active');
    document.body.style.overflow = '';
  }

  // ── JOB DESCRIPTION MODAL ──
  function openJobDesc(card) {
    const id         = card.dataset.recId;
    const title      = card.dataset.recTitle;
    const company    = card.dataset.recCompany;
    const vacancy    = card.dataset.recVacancy;
    const department = card.dataset.recDepartment;
    const position   = card.dataset.recPosition;
    const employment = card.dataset.recEmployment;
    const location   = card.dataset.recLocation;
    const workmode   = card.dataset.recWorkmode;
    const priority   = card.dataset.recPriority;
    const budget     = card.dataset.recBudget;

    const descEl = card.querySelector('.job-desc-html');
    const raw    = descEl ? descEl.innerHTML.trim() : '';
    const html   = raw || '<p style="color:var(--gray-500);font-style:italic;">No job description provided.</p>';

    document.getElementById('jobDescTitle').textContent = title;

    // Build meta badges
    const meta = document.getElementById('jobDescMeta');
    meta.innerHTML = '';
    const badges = [company, department, position, employment, location, workmode, priority ? 'Priority: ' + priority : '', budget ? 'Budget: ' + budget : '', vacancy ? vacancy + ' positions' : ''];
    badges.forEach(function(text) {
      if (text && text.trim()) {
        const s = document.createElement('span');
        s.textContent = text.trim();
        meta.appendChild(s);
      }
    });

    // Build detail table above JD
    const details = [];
    if (department)  details.push(['Department',       department]);
    if (position)    details.push(['Position',         position]);
    if (employment)  details.push(['Employment Type',  employment]);
    if (location)    details.push(['Location',         location]);
    if (workmode)    details.push(['Work Mode',        workmode]);
    if (priority)    details.push(['Priority',         priority]);
    if (budget)      details.push(['Budget',           budget]);
    if (vacancy)     details.push(['Vacancies',        vacancy]);

    let detailsHtml = '';
    if (details.length) {
      detailsHtml = '<table style="width:100%;border-collapse:collapse;margin-bottom:1.25rem;font-size:.9rem;">';
      details.forEach(function(row) {
        detailsHtml += '<tr><td style="padding:5px 0;color:var(--gray-500);width:40%;vertical-align:top">' + row[0] + '</td>'
                     + '<td style="padding:5px 0;font-weight:600;color:var(--gray-700)">' + row[1] + '</td></tr>';
      });
      detailsHtml += '</table><hr style="border:none;border-top:1px solid var(--green-100);margin-bottom:1.25rem;">';
    }

    document.getElementById('jobDescContent').innerHTML = detailsHtml + html;

    document.getElementById('jobDescApplyBtn').onclick = function() {
      closeJobDesc();
      openApplicationModal(id, title);
    };

    document.getElementById('jobDescModal').classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeJobDesc() {
    document.getElementById('jobDescModal').classList.remove('active');
    document.body.style.overflow = '';
  }

  document.getElementById('jobDescModal').addEventListener('click', function(e) {
    if (e.target === this) closeJobDesc();
  });

  // ✅ SAFER: attach click listeners instead of inline onclick
  document.querySelectorAll('.apply-link').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();

      const card = this.closest('.job-card');
      const id = card.dataset.recId;
      const titleEl = card.querySelector('.job-title');
      const title = titleEl ? titleEl.textContent.trim() : 'Apply';

      if (id) {
        openApplicationModal(id, title);
      }
    });
  });

  // Close on backdrop click
  document.getElementById('applicationModal').addEventListener('click', function(e) {
    if (e.target === this) closeApplicationModal();
  });

  // Close on Escape key
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') { closeApplicationModal(); closeJobDesc(); }
  });

  // Form submit
  var form = document.getElementById('careerApplicationForm');

  if (form) {
    form.addEventListener('submit', function(e) {
      e.preventDefault();

      var btn = document.getElementById('submitBtn');
      btn.disabled = true;
      btn.textContent = 'Submitting…';

      var formData = new FormData(form);

      var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
      if (csrfToken) {
        formData.append('csrfmiddlewaretoken', csrfToken.value);
      }

      fetch('/recruitment/api/apply/', {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        body: formData
      })
      .then(async function (r) {
        let data;

        try {
          data = await r.json();
        } catch (e) {
          throw new Error("Invalid server response");
        }

        if (!r.ok) {
          throw new Error(data?.error || data?.message || "Submission failed");
        }

        return data;
      })
      .then(function(data) {
        form.reset();
        form.style.display = 'none';
        document.getElementById('applicationSuccessMessage').style.display = 'block';
        document.getElementById('modalFooter').style.display = 'none';
      })
      .catch(function(error) {
        alert('Error submitting application: ' + error.message);
      })
      .finally(function() {
        btn.disabled = false;
        btn.textContent = 'Submit application';
      });
    });
  }
</script>
</body>
</html>