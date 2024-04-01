from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

class AbstractDatestamp(models.Model):
    date_created = models.DateTimeField(auto_now_add=True, verbose_name=_("Date created"))
    date_updated = models.DateTimeField(auto_now=True, verbose_name=_("Date updated"))

    class Meta:
        abstract = True



class AcademicYear(models.Model):
    year = models.IntegerField(
        unique=True,
        help_text=_("Academic year."),
        verbose_name=_("Year")
    )

    def __str__(self):
        return str(self.year)

    class Meta:
        verbose_name = _("Academic year")
        verbose_name_plural = _("Academic years")


class Institution(MPTTModel):
    name = models.CharField(
        max_length=100,
        help_text=_("Name of the institution."),
        verbose_name=_("Name")
    )
    parent = TreeForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='children',
        db_index=True,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = _("Institution")
        verbose_name_plural = _("Institutions")


class Faculty(MPTTModel):
    name = models.CharField(
        max_length=100,
        help_text=_("Name of the faculty."),
        verbose_name=_("Name")
    )
    parent = TreeForeignKey(
        'Institution',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = _("Faculty")
        verbose_name_plural = _("Faculties")


class EducationalProgram(models.Model):
    name = models.CharField(
        max_length=100,
        help_text=_("Name of the educational program."),
        verbose_name=_("Name")
    )
    faculty = models.ForeignKey(
        'Faculty',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Educational program")
        verbose_name_plural = _("Educational programs")


class StudyGroup(AbstractDatestamp):
    name = models.CharField(
        max_length=16,
        help_text=_("Name of the study group."),
        verbose_name=_("Name")
    )
    academic_year = models.ForeignKey(
        'AcademicYear',
        on_delete=models.CASCADE,
        null= True
    )
    educational_program = models.ForeignKey(
        'EducationalProgram',
        on_delete=models.CASCADE,
        null= True
    )

    is_active = models.BooleanField(
        default=True,
        help_text=_("Determines whether an entity is active in the system."),
        verbose_name=_("Active")
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Study group")
        verbose_name_plural = _("Study groups")


class Student(AbstractDatestamp):
    guid = models.CharField(
        max_length=36,
        unique=True,
        db_index=True,
        help_text=_("GUID of the student."),
        verbose_name=_("GUID")
    )
    name = models.CharField(
        max_length=128,
        help_text=_("Full name of the student."),
        verbose_name=_("Full name")
    )
    study_group = models.ForeignKey(
        StudyGroup,
        on_delete=models.CASCADE,
        help_text=_("Name of the study group."),
        verbose_name=_("Study group")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Determines whether an entity is active in the system."),
        verbose_name=_("Active")
    )

    def __str__(self):
        return f"({self.study_group}) {self.name}"

    class Meta:
        verbose_name = _("Student")
        verbose_name_plural = _("Students")


class StudyGroupOld(AbstractDatestamp):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        help_text=_("Full name of the student."),
        verbose_name=_("Full name")
    )
    study_group = models.ForeignKey(
        StudyGroup,
        on_delete=models.CASCADE,
        help_text=_("Name of the study group."),
        verbose_name=_("Study group")
    )
    date_start = models.DateField(
        help_text=_("The beginning of studies in this group."),
        verbose_name=_("Date start")
    )
    date_end = models.DateField(
        help_text=_("The end of studies in this group."),
        verbose_name=_("Date end")
    )

    def __str__(self):
        return self.study_group.name

    class Meta:
        verbose_name = _("Old Study group")
        verbose_name_plural = _("Old Study groups")


class ScheduleType(AbstractDatestamp):
    name = models.CharField(
        max_length=8,
        unique=True,
        db_index=True,
        help_text=_("Name of the type of schedule."),
        verbose_name=_("Name")
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Schedule type")
        verbose_name_plural = _("Schedule types")


class Schedule(AbstractDatestamp):
    study_group = models.ForeignKey(
        StudyGroup,
        on_delete=models.CASCADE,
        help_text=_("Name of the study group."),
        verbose_name=_("Study group")
    )
    type = models.ForeignKey(
        ScheduleType,
        on_delete=models.CASCADE,
        help_text=_("Name of the type of schedule."),
        verbose_name=_("Type")
    )
    is_session = models.BooleanField(
        default=False,
        help_text=_("Determines whether the schedule is a session schedule or not."),
        verbose_name=_("Session")
    )
    date_start = models.DateField(
        help_text=_("The start date of the schedule."),
        verbose_name=_("Date start")
    )
    date_end = models.DateField(
        help_text=_("The end date of the schedule."),
        verbose_name=_("Date end")
    )
    grid = models.JSONField(
        help_text=_("Raw schedule grid format."),
        verbose_name=_("Grid")
    )
    signature = models.CharField(
        max_length=32,
        unique=True,
        db_index=True,
        help_text=_("The unique identifier of the schedule based on its data."),
        verbose_name=_("Signature")
    )

    def __str__(self):
        return f"{self.study_group} ({self.date_start.strftime('%d.%m.%Y')}-{self.date_end.strftime('%d.%m.%Y')})"

    class Meta:
        verbose_name = _("Schedule")
        verbose_name_plural = _("Schedules")


class HistoryLog(AbstractDatestamp):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text=_("The user who performed the action."),
        verbose_name=_("User")
    )
    action = models.CharField(
        max_length=128,
        help_text=_("Action in the system."),
        verbose_name=_("Action")
    )

    def __str__(self):
        local_date = timezone.localtime(self.date_created)
        return f"{self.user}" + " " + _("action") + f" ({local_date.strftime('%d.%m.%Y %H:%M')})"

    class Meta:
        verbose_name = _("History Log")
        verbose_name_plural = _("History Logs")


HistoryLog._meta.get_field("date_created").verbose_name = _("Date")
