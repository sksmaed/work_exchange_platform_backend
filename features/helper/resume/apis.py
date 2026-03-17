from typing import Any

from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import get_object_or_404
from ninja_extra import api_controller, route
from ninja_extra.permissions import IsAuthenticated

from features.helper.models import HelperModel
from features.helper.resume.models import HelperResume
from features.helper.resume.schemas import ResumeCreate, ResumeOut, ResumeUpdate


@api_controller(
    prefix_or_class="helper/resume",
    tags=["helper_resume"],
    permissions=[IsAuthenticated],
)
class HelperResumeAPI:
    """API for helper resume CRUD for the authenticated user."""

    @route.get("/self/", response={200: ResumeOut}, url_name="get_self_resume")
    def get_self_resume(self, request: WSGIRequest):
        """Retrieve the authenticated user's resume."""
        helper = get_object_or_404(HelperModel, user=request.user)
        resume = get_object_or_404(HelperResume, helper=helper)
        return 200, self._to_schema(resume)

    @route.post("/", response={201: ResumeOut}, url_name="create_resume")
    def create_resume(self, request: WSGIRequest, payload: ResumeCreate):
        """Create a new resume for the authenticated user."""
        helper = get_object_or_404(HelperModel, user=request.user)
        resume = HelperResume.objects.create(
            helper=helper,
            title=payload.title or "",
            summary=payload.summary or "",
            experiences=payload.experiences or [],
            skills=payload.skills or [],
            certifications=payload.certifications or [],
            availability=payload.availability or [],
            preferred_locations=payload.preferred_locations or [],
            contact_email=payload.contact_email or "",
            contact_phone=payload.contact_phone or "",
        )
        return 201, self._to_schema(resume)

    @route.put("/", response={200: ResumeOut}, url_name="update_resume")
    def update_resume(self, request: WSGIRequest, payload: ResumeUpdate):
        """Update the authenticated user's resume."""
        helper = get_object_or_404(HelperModel, user=request.user)
        resume = get_object_or_404(HelperResume, helper=helper)

        update_fields: list[str] = []
        for field in (
            "title",
            "summary",
            "experiences",
            "skills",
            "certifications",
            "availability",
            "preferred_locations",
            "contact_email",
            "contact_phone",
        ):
            value: Any = getattr(payload, field)
            if value is not None:
                setattr(resume, field, value)
                update_fields.append(field)
        if update_fields:
            resume.save(update_fields=update_fields)
        return 200, self._to_schema(resume)

    def _to_schema(self, resume: HelperResume) -> ResumeOut:
        return ResumeOut(
            id=str(resume.id),
            title=resume.title,
            summary=resume.summary,
            experiences=resume.experiences,
            skills=resume.skills,
            certifications=resume.certifications,
            availability=resume.availability,
            preferred_locations=resume.preferred_locations,
            contact_email=resume.contact_email,
            contact_phone=resume.contact_phone,
        )
