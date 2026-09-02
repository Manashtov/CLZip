import json
from pathlib import Path
from PyQt6.QtCore import QSettings

settings = QSettings("clzip", "Settings")

TRANSLATIONS = {
    "es": {
        "col_name": "Nombre",
        "col_size": "Tamaño",
        "col_type": "Tipo",
        "col_modified": "Modificado",
        "btn_extract": " Extraer",
        "btn_compress": " Comprimir",
        "btn_home": " Inicio",
        "btn_up": " Subir",
        "btn_refresh": " Actualizar",
        "btn_theme": " Tema",
        "btn_lang": " Idioma",
        "btn_settings": " Ajustes",
        "bm_home": "Usuario",
        "bm_desktop": "Escritorio",
        "bm_documents": "Documentos",
        "bm_downloads": "Descargas",
        "ctx_compress": "Comprimir archivo(s)...",
        "ctx_extract": "Extraer en carpeta...",
        "ctx_copy": "Copiar",
        "ctx_paste": "Pegar",
        "ctx_select_all": "Seleccionar todo",
        "ctx_password": "Establecer / Modificar Contraseña",
        "ctx_checksum": "Verificar Checksum (SHA-256)",
        "ctx_open_terminal": "Abrir en Terminal",
        "ctx_open_folder": "Abrir en Explorador de Windows",
        "ctx_delete": "Eliminar",
        "ctx_delete_confirm": "¿Mover {count} elemento(s) a la Papelera de Reciclaje?",
        "ctx_delete_error": "Error al eliminar {name}: {error}",
        "ctx_properties": "Propiedades",
        "err_access_folder": "No se puede acceder a la carpeta:\n{error}",
        "err_paste": "Error al pegar {name}:\n{error}",
        "pwd_protect_title": "Proteger {name}",
        "pwd_protect_prompt": "Ingresa la contraseña para cifrar:",
        "pwd_set_title": "Contraseña de Sesión",
        "pwd_set_prompt": "Ingresa la contraseña por defecto:",
        "pwd_current_title": "Archivo Protegido",
        "pwd_current_prompt": "Ingresa la contraseña actual:",
        "pwd_active": "Contraseña activa configurada.",
        "pwd_cleared": "Contraseña eliminada.",
        "status_zip_stage": "Procesando",
        "status_tar_stage": "Creando contenedor TAR",
        "status_zstd_stage": "Comprimiendo con Zstandard",
        "status_extract_stage": "Descomprimiendo archivos",
        "status_recrypt_unpack": "Desempaquetando para cifrado",
        "status_recrypt_pack": "Aplicando cifrado AES-256",
        "status_vel": "Vel.",
        "status_elapsed": "Transcurrido",
        "status_remaining": "Restante",
        "status_completed": "Operación finalizada con éxito en {time}s",
        "recrypt_success": "{count} archivos recifrados correctamente.",
        "settings_saved": "Configuración guardada exitosamente.",
        "settings_title": "Configuración de CLZip",
        "tab_shortcuts": "Atajos",
        "tab_appearance": "Apariencia",
        "tab_info": "Info",
        "shortcuts_hint": "Haz clic sobre cualquier campo para ingresar una nueva combinación de teclas:",
        "col_action": "Acción",
        "col_shortcut": "Atajo Asignado",
        "palette_group": "Paleta de Color Primario",
        "palette_hint": "Selecciona la combinación cromática de acento para botones, selecciones y navegación:",
        "btn_reset": "Restablecer predeterminado",
        "btn_apply": "Aplicar",
        "btn_cancel": "Cancelar",
        "info_app_desc": "Gestor y Archivador de Archivos de Alto Rendimiento",
        "info_author": "Desarrollador:",
        "info_tech": "Tecnologías:",
        "info_license": "Licencia:",
        "ctx_remove_password": "Quitar contraseña...",
        "pwd_remove_title": "Quitar Contraseña: {name}",
        "pwd_remove_success": "✓ Contraseña eliminada con éxito."
    },
    "en": {
        "col_name": "Name",
        "col_size": "Size",
        "col_type": "Type",
        "col_modified": "Modified",
        "btn_extract": " Extract",
        "btn_compress": " Compress",
        "btn_home": " Home",
        "btn_up": " Up",
        "btn_refresh": " Refresh",
        "btn_theme": " Theme",
        "btn_lang": " Language",
        "btn_settings": " Settings",
        "bm_home": "User",
        "bm_desktop": "Desktop",
        "bm_documents": "Documents",
        "bm_downloads": "Downloads",
        "ctx_compress": "Compress file(s)...",
        "ctx_extract": "Extract to folder...",
        "ctx_copy": "Copy",
        "ctx_paste": "Paste",
        "ctx_select_all": "Select all",
        "ctx_password": "Set / Modify Password",
        "ctx_checksum": "Verify Checksum (SHA-256)",
        "ctx_open_terminal": "Open in Terminal",
        "ctx_open_folder": "Open in File Explorer",
        "ctx_delete": "Delete",
        "ctx_delete_confirm": "Move {count} item(s) to the Recycle Bin?",
        "ctx_delete_error": "Error deleting {name}: {error}",
        "ctx_properties": "Properties",
        "err_access_folder": "Cannot access directory:\n{error}",
        "err_paste": "Error pasting {name}:\n{error}",
        "pwd_protect_title": "Protect {name}",
        "pwd_protect_prompt": "Enter password to encrypt:",
        "pwd_set_title": "Session Password",
        "pwd_set_prompt": "Enter default password:",
        "pwd_current_title": "Protected Archive",
        "pwd_current_prompt": "Enter current password:",
        "pwd_active": "Active password configured.",
        "pwd_cleared": "Password cleared.",
        "status_zip_stage": "Processing",
        "status_tar_stage": "Creating TAR container",
        "status_zstd_stage": "Compressing with Zstandard",
        "status_extract_stage": "Extracting files",
        "status_recrypt_unpack": "Unpacking for encryption",
        "status_recrypt_pack": "Applying AES-256 encryption",
        "status_vel": "Speed",
        "status_elapsed": "Elapsed",
        "status_remaining": "Remaining",
        "status_completed": "Operation completed successfully in {time}s",
        "recrypt_success": "{count} files re-encrypted successfully.",
        "settings_saved": "Settings saved successfully.",
        "settings_title": "CLZip Settings",
        "tab_shortcuts": "Shortcuts",
        "tab_appearance": "Appearance",
        "tab_info": "About",
        "shortcuts_hint": "Click on any field to enter a new key combination:",
        "col_action": "Action",
        "col_shortcut": "Assigned Shortcut",
        "palette_group": "Primary Color Palette",
        "palette_hint": "Select the accent chromatic theme for buttons, selections, and navigation:",
        "btn_reset": "Restore Default",
        "btn_apply": "Apply",
        "btn_cancel": "Cancel",
        "info_app_desc": "High-Performance File Manager & Archiver",
        "info_author": "Developer:",
        "info_tech": "Technologies:",
        "info_license": "License:",
        "ctx_remove_password": "Remove password...",
        "pwd_remove_title": "Remove Password: {name}",
        "pwd_remove_success": "✓ Password removed successfully.",
    }
}

class I18nManager:
    _current_locale: str = settings.value("language", "es", type=str)

    @classmethod
    def get_locale(cls) -> str:
        return cls._current_locale

    @classmethod
    def set_locale(cls, locale_code: str):
        cls._current_locale = locale_code
        settings.setValue("language", locale_code)

    @classmethod
    def translate(cls, key: str, **kwargs) -> str:
        lang = cls.get_locale()
        locale_dict = TRANSLATIONS.get(lang, TRANSLATIONS.get("es", {}))
        text = locale_dict.get(key, TRANSLATIONS["es"].get(key, key))
        if kwargs:
            try:
                return text.format(**kwargs)
            except Exception:
                return text
        return text

def get_locale() -> str:
    return I18nManager.get_locale()

def set_locale(locale_code: str):
    I18nManager.set_locale(locale_code)

def tr(key: str, **kwargs) -> str:
    return I18nManager.translate(key, **kwargs)