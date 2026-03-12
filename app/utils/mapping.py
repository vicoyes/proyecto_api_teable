from app.schemas.projects import ProjectResponse
from app.schemas.tasks import LinkedRecordRef, TaskResponse
from app.schemas.team import TeamMemberResponse
from app.schemas.clientes import ClienteResponse
from app.schemas.correos import CorreoResponse


def map_linked_record(value):
    if isinstance(value, dict) and value.get("id"):
        return LinkedRecordRef(
            id=value["id"],
            title=value.get("title"),
        )

    return None


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
        responsable=map_linked_record(fields.get("responsable")),
        proyecto=map_linked_record(fields.get("proyecto")),
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

def map_cliente_record(record: dict) -> ClienteResponse:
    fields = record.get("fields", {})
    return ClienteResponse(
        id=record["id"],
        etiqueta=fields.get("Etiqueta"),
        nombre_del_cliente=fields.get("Nombre del Cliente"),
        email=fields.get("Email"),
        empresa=fields.get("Empresa"),
        numero_de_telefono=fields.get("Numero de telefono"),
        notas=fields.get("Notas"),
    )


def map_correo_record(record: dict) -> CorreoResponse:
    fields = record.get("fields", {})
    return CorreoResponse(
        id=record["id"],
        date_iso=fields.get("date_iso"),
        from_name=fields.get("from_name"),
        from_email=fields.get("from_email"),
        to_email=fields.get("to_email"),
        subject=fields.get("subject"),
        body_clean=fields.get("body_clean"),
        status=fields.get("status"),
        proposed_reply=fields.get("proposed_reply"),
        approval_status=fields.get("approval_status"),
        approved_reply=fields.get("approved_reply"),
        responded=fields.get("responded"),
        thread_key=fields.get("thread_key"),
        notes=fields.get("notes"),
        ai_summary=fields.get("ai_summary"),
        ai_sentiment=fields.get("ai_sentiment"),
        ai_intent=fields.get("ai_intent"),
        ai_priority=fields.get("ai_priority"),
        ai_requires_reply=fields.get("ai_requires_reply"),
        ai_category=fields.get("ai_category"),
        remitente_original_email=fields.get("remitente_original_email"),
        nombre_del_remitente_original=fields.get("nombre_del_remitente_original"),
        Tipo=fields.get("Tipo"),
    )
