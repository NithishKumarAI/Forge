from sqlmodel import Session, select

from ..models import AppSetting, Curriculum


ACTIVE_CURRICULUM_KEY = "active_curriculum_id"


def get_active_curriculum(session: Session) -> Curriculum | None:
    setting = session.get(AppSetting, ACTIVE_CURRICULUM_KEY)
    if setting:
        try:
            curriculum = session.get(Curriculum, int(setting.value))
        except ValueError:
            curriculum = None
        if curriculum is not None and curriculum.status == "confirmed":
            return curriculum
    return session.exec(
        select(Curriculum)
        .where(Curriculum.status == "confirmed")
        .order_by(Curriculum.created_at)
    ).first()


def activate_curriculum(session: Session, curriculum: Curriculum) -> None:
    if curriculum.status != "confirmed":
        raise ValueError("Only a confirmed curriculum can become active")
    setting = session.get(AppSetting, ACTIVE_CURRICULUM_KEY)
    if setting is None:
        setting = AppSetting(key=ACTIVE_CURRICULUM_KEY, value=str(curriculum.id))
    else:
        setting.value = str(curriculum.id)
    session.add(setting)
    session.commit()
