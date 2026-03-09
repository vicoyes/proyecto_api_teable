from app.schemas.projects import ProjectResponse
from app.schemas.tasks import TaskResponse
from app.schemas.team import TeamMemberResponse


def map_task_record(record: dict) -> TaskResponse:
    fields = record.get("fields", {})
    return TaskResponse(
        id=record["id"],
        nombre_tarea=fields.get("nombre_tarea"),
        prioridad=fields.get("prioridad"),
        estado_tarea=fields.get("estado_tarea"),
        tipo_tarea=fields.get("tipo_tarea"),
        fecha_limite=fields.get("fecha_limite"),
        fecha_creacion=fields.get("fecha_creacion"),
        fecha_inicio=fields.get("fecha_inicio"),
        fecha_cierre=fields.get("fecha_cierre"),
        hh_estimadas=fields.get("hh_estimadas"),
        hh_reales=fields.get("hh_reales"),
        notas=fields.get("notas"),
        correcciones=fields.get("correcciones"),
        resultado=fields.get("resultado"),
        evidencias=fields.get("evidencias"),
        responsable=fields.get("responsable"),
        proyecto=fields.get("proyecto"),
    )


def map_team_record(record: dict) -> TeamMemberResponse:
    fields = record.get("fields", {})
    return TeamMemberResponse(
        id=record["id"],
        nombre=fields.get("nombre"),
        tipo_miembro=fields.get("tipo_miembro"),
        rol=fields.get("rol"),
        especialidad=fields.get("especialidad"),
        estado=fields.get("estado"),
        capacidad_horas=fields.get("capacidad_horas"),
        canal_contacto=fields.get("canal_contacto"),
        notas=fields.get("notas"),
    )


def map_project_record(record: dict) -> ProjectResponse:
    fields = record.get("fields", {})
    return ProjectResponse(
        id=record["id"],
        nombre_proyecto=fields.get("nombre_proyecto"),
        cliente=fields.get("cliente"),
        tipo_proyecto=fields.get("tipo_proyecto"),
        estado_proyecto=fields.get("estado_proyecto"),
        prioridad_proyecto=fields.get("prioridad_proyecto"),
        responsable_general=fields.get("responsable_general"),
        descripcion=fields.get("descripcion"),
        fecha_inicio=fields.get("fecha_inicio"),
        fecha_fin=fields.get("fecha_fin"),
    )
