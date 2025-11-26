from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from auth.database import get_db
from auth.models import User
from dependencies import get_current_user # Importar dependencia de auth
from . import models, schemas
import llm_service

router = APIRouter(
    prefix="/api/chat",
    tags=["chat"]
)

# --- Conversations ---

@router.post("/conversations", response_model=schemas.ConversationResponse)
def create_conversation(
    conversation: schemas.ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crea una nueva conversación"""
    db_conversation = models.Conversation(
        user_id=current_user.id,
        title=conversation.title or "New Conversation"
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

@router.get("/conversations", response_model=List[schemas.ConversationResponse])
def get_conversations(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene todas las conversaciones del usuario"""
    conversations = db.query(models.Conversation)\
        .filter(models.Conversation.user_id == current_user.id)\
        .order_by(models.Conversation.updated_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    return conversations

@router.get("/conversations/{conversation_id}", response_model=schemas.ConversationDetail)
def get_conversation_detail(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene una conversación con sus mensajes"""
    conversation = db.query(models.Conversation)\
        .filter(models.Conversation.id == conversation_id, models.Conversation.user_id == current_user.id)\
        .first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    print(f"🔍 [DEBUG] Get Conversation {conversation_id}: {len(conversation.messages)} messages found.")
    for msg in conversation.messages:
        print(f"   - [{msg.role}] {msg.content[:50]}...")

    return conversation

@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Elimina una conversación"""
    conversation = db.query(models.Conversation)\
        .filter(models.Conversation.id == conversation_id, models.Conversation.user_id == current_user.id)\
        .first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    db.delete(conversation)
    db.commit()
    return {"message": "Conversation deleted"}

# --- Messages ---

@router.post("/conversations/{conversation_id}/messages", response_model=schemas.MessageResponse)
def create_message(
    conversation_id: int,
    message: schemas.MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Agrega un mensaje a la conversación.
    Si el rol es 'user', opcionalmente se podría disparar una respuesta del bot aquí.
    """
    # Verificar que la conversación existe y pertenece al usuario
    conversation = db.query(models.Conversation)\
        .filter(models.Conversation.id == conversation_id, models.Conversation.user_id == current_user.id)\
        .first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Guardar mensaje del usuario
    db_message = models.Message(
        conversation_id=conversation_id,
        role=message.role,
        content=message.content
    )
    db.add(db_message)
    
    # Actualizar timestamp de la conversación
    from datetime import datetime
    conversation.updated_at = datetime.utcnow()
    
    # Si es el primer mensaje y el título es default, actualizar título
    if len(conversation.messages) == 0 and conversation.title == "New Conversation":
        # Generar título simple (primeras 5 palabras)
        conversation.title = " ".join(message.content.split()[:5])
        
    db.commit()
    db.refresh(db_message)

    # --- LÓGICA DE GENERACIÓN Y PUBLICACIÓN DE CONTENIDO ---
    if message.role == "user" and message.selected_networks:
        import social_services # Importar aquí para evitar ciclos si los hubiera
        import httpx
        import os
        import tempfile

        try:
            # 1. Validar contenido (opcional, pero recomendado)
            validacion = llm_service.validar_contenido_academico(message.content)
            
            if not validacion.get("es_academico", False):
                # Si no es académico, responder con la razón
                razon = validacion.get("razon", "Contenido no apropiado.")
                assistant_content = f"⚠️ El contenido no parece ser académico o relacionado con la UAGRM.\n\nRazón: {razon}"
                
                # Guardar respuesta de error/advertencia
                error_msg = models.Message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=assistant_content
                )
                db.add(error_msg)
                db.commit()
                return db_message 
                
            else:
                # 2. Generar y Publicar contenido para cada red
                resultados = []
                for red in message.selected_networks:
                    print(f"🔄 Procesando red: {red}...")
                    
                    # A. ADAPTACIÓN
                    adaptacion = llm_service.adaptar_contenido(
                        titulo="Generación Automática", 
                        contenido=message.content,
                        red_social=red
                    )
                    
                    if "error" in adaptacion:
                        resultados.append({
                            "network": red,
                            "content": adaptacion,
                            "status": "error",
                            "error": adaptacion["error"]
                        })
                        continue

                    # B. GENERACIÓN DE MEDIA (Imagen/Video)
                    media_url = None
                    video_urls = []
                    video_path = None
                    
                    # Instagram/Facebook: Generar Imagen (URL pública)
                    if red in ["instagram", "facebook"] and "suggested_image_prompt" in adaptacion:
                         print(f"🎨 Generando imagen para {red}...")
                         url_imagen = llm_service.generar_imagen_ia(adaptacion["suggested_image_prompt"])
                         adaptacion["image_url"] = url_imagen
                         media_url = url_imagen
                    
                    # WhatsApp: Generar Imagen (Base64 para evitar errores de enlace)
                    if red == "whatsapp" and "suggested_image_prompt" in adaptacion:
                         print(f"🎨 Generando imagen para {red} (Base64)...")
                         # Usar Base64 para WhatsApp
                         url_imagen = llm_service.generar_imagen_ia_base64(adaptacion["suggested_image_prompt"])
                         adaptacion["image_url"] = url_imagen
                         media_url = url_imagen
                    
                    # TikTok: Generar Video con Audio
                    if red == "tiktok":
                        print(f"🎬 Generando video COMPLETO para TikTok (con audio)...")
                        # Usar la función completa de llm_service que genera audio y combina
                        video_path = llm_service.generar_video_tiktok(message.content, adaptacion)
                        
                        if video_path:
                            adaptacion["video_generated_path"] = video_path
                            # Simular URL para mostrar en frontend (aunque es local)
                            adaptacion["video_urls"] = ["(Video generado localmente con audio)"]
                        else:
                            adaptacion["error"] = "Falló la generación de video"

                    # C. PUBLICACIÓN
                    publicacion_result = None
                    texto_final = adaptacion.get("text", "")
                    
                    try:
                        if red == "facebook":
                            publicacion_result = social_services.post_to_facebook(texto_final, media_url)
                        
                        elif red == "instagram":
                            if media_url:
                                publicacion_result = social_services.post_to_instagram(texto_final, media_url)
                            else:
                                publicacion_result = {"error": "No se pudo generar imagen para Instagram"}

                        elif red == "linkedin":
                            publicacion_result = social_services.post_to_linkedin(texto_final)

                        elif red == "whatsapp":
                            publicacion_result = social_services.post_whatsapp_status(texto_final, media_url)

                        elif red == "tiktok":
                            if video_path and os.path.exists(video_path):
                                publicacion_result = social_services.post_to_tiktok(texto_final, video_path)
                                # No borramos el video inmediatamente por si se necesita debug, o lo borramos después
                                # os.remove(video_path) 
                            else:
                                publicacion_result = {"error": "No se pudo generar el video para TikTok"}

                    except Exception as e:
                        print(f"❌ Error publicando en {red}: {e}")
                        publicacion_result = {"error": str(e)}

                    resultados.append({
                        "network": red,
                        "content": adaptacion,
                        "publish_result": publicacion_result
                    })

                # 3. Formatear respuesta del asistente
                response_text = "He procesado tu solicitud para las redes seleccionadas:\n\n"
                
                for res in resultados:
                    red = res['network'].capitalize()
                    content_data = res.get('content', {})
                    pub_result = res.get('publish_result', {})
                    
                    response_text += f"### {red}\n"
                    
                    # Estado de publicación
                    if pub_result and "error" not in pub_result:
                        link = pub_result.get("permalink") or pub_result.get("share_url") or pub_result.get("link")
                        
                        # Construir link manual para Facebook si no viene en la respuesta
                        if not link and res['network'] == 'facebook' and 'id' in pub_result:
                            # El ID suele ser PAGEID_POSTID o solo POSTID
                            post_id = pub_result['id']
                            # Si el ID tiene formato PAGE_POST, extraemos la parte del post
                            if '_' in post_id:
                                _, post_id = post_id.split('_')
                            link = f"https://www.facebook.com/{post_id}"

                        if link:
                            response_text += f"✅ **Publicado exitosamente**: [Ver Publicación]({link})\n\n"
                        else:
                            response_text += f"✅ **Publicado exitosamente** (ID: {pub_result.get('id', 'N/A')})\n\n"
                    else:
                        error_msg = pub_result.get("error") if pub_result else "Error desconocido"
                        response_text += f"❌ **Error al publicar**: {error_msg}\n\n"

                    # Mostrar contenido generado
                    text_body = content_data.get('text', '')
                    response_text += f"**Contenido Generado:**\n{text_body}\n\n"
                    
                    if "image_url" in content_data:
                        response_text += f"![Imagen Generada]({content_data['image_url']})\n"
                        
                    if "video_generated_path" in content_data:
                        response_text += f"**Video Generado con Audio** (Subido a TikTok)\n"
                    elif "video_urls" in content_data:
                        response_text += f"**Video Fuente:** [Ver Video Original]({content_data['video_urls'][0]})\n"
                    
                    response_text += "\n---\n\n"

                # Guardar mensaje del asistente
                assistant_msg = models.Message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=response_text
                )
                db.add(assistant_msg)
                db.commit()

        except Exception as e:
            print(f"Error generando contenido: {e}")
            import traceback
            traceback.print_exc()
            # Guardar mensaje de error
            error_msg = models.Message(
                conversation_id=conversation_id,
                role="assistant",
                content=f"Lo siento, hubo un error al procesar tu solicitud: {str(e)}"
            )
            db.add(error_msg)
            db.commit()
    
    return db_message
