from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import os
from recruitment.cv_screening_ai import CVScreeningAI
from recruitment.cv_screening_fallback import mock_analyze_cv


@login_required
def job_board_settings(request):
    return render(request, "recruitment/job_board_settings.html")


@login_required
@csrf_exempt
def cv_screening(request):
    if request.method == 'POST':
        try:
            # Handle file upload
            cv_file = request.FILES.get('cv_file')
            job_requirements = request.POST.get('job_requirements', '')

            if not cv_file:
                return JsonResponse({'error': 'No CV file provided'}, status=400)

            if not job_requirements:
                return JsonResponse({'error': 'Job requirements are required'}, status=400)

            # Create temp file path
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'_{cv_file.name}') as temp_file:
                for chunk in cv_file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name

            try:
                # Extract content
                ai = CVScreeningAI()
                cv_content = ai.extract_cv_content(temp_file_path)

                # Analyze with AI - try API first, fallback to mock
                analysis = ai.analyze_cv_with_deepseek(cv_content, job_requirements)
                
                # If API fails, use fallback analyzer
                if not analysis:
                    print(f"API call failed, using fallback analyzer")
                    analysis = mock_analyze_cv(cv_content, job_requirements)

                if analysis:
                    return JsonResponse({
                        'candidate_name': analysis.get('candidate_name', 'Unknown'),
                        'skills': analysis.get('skills', []),
                        'years_experience': analysis.get('years_experience', 0),
                        'education': analysis.get('education', []),
                        'matching_score': analysis.get('matching_score', 0),
                        'matching_skills': analysis.get('matching_skills', []),
                        'missing_skills': analysis.get('missing_skills', []),
                        'summary': analysis.get('summary', ''),
                        'recommendation': analysis.get('recommendation', 'interview')
                    })
                else:
                    return JsonResponse({'error': 'AI analysis failed'}, status=500)

            finally:
                # Clean up temp file
                import os
                os.unlink(temp_file_path)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)

    return render(request, "recruitment/cv_screening.html")


@login_required
def candidate_evaluation(request):
    return render(request, "recruitment/candidate_evaluation.html")
