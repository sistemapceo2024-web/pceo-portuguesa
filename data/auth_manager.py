"""
Gestor de Autenticación, Usuarios y Auditoría (SIGSO - PCEO)
Puesto de Comando Estratégico Operacional del Estado Portuguesa
"""
import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple

USUARIOS_JSON_PATH = os.path.join(os.path.dirname(__file__), "usuarios.json")
AUDITORIA_JSON_PATH = os.path.join(os.path.dirname(__file__), "auditoria.json")

def hash_password(password: str) -> str:
    """Genera hash SHA-256 seguro para contraseñas."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

# Perfiles iniciales oficiales predeterminados requeridos
DEFAULT_USERS = [
    # 2 Usuarios Master
    {
        "username": "master1",
        "nombre": "Manuel Hidalgo — Coordinación PCEO",
        "password_hash": hash_password("Pceo2026*"),
        "rol": "MASTER",
        "activo": True,
        "fecha_creacion": "2026-11-12 08:00:00",
        "ultimo_acceso": "2026-11-13 00:00:00"
    },
    {
        "username": "master2",
        "nombre": "Coordinador Adjunto PCEO",
        "password_hash": hash_password("Pceo2026*"),
        "rol": "MASTER",
        "activo": True,
        "fecha_creacion": "2026-11-12 08:00:00",
        "ultimo_acceso": "2026-11-12 18:30:00"
    },
    # 3 Usuarios Analistas
    {
        "username": "analista1",
        "nombre": "Analista de Sala 1",
        "password_hash": hash_password("Sala2026*"),
        "rol": "ANALISTA",
        "activo": True,
        "fecha_creacion": "2026-11-12 08:00:00",
        "ultimo_acceso": "2026-11-12 21:15:00"
    },
    {
        "username": "analista2",
        "nombre": "Analista de Sala 2",
        "password_hash": hash_password("Sala2026*"),
        "rol": "ANALISTA",
        "activo": True,
        "fecha_creacion": "2026-11-12 08:00:00",
        "ultimo_acceso": "2026-11-12 19:40:00"
    },
    {
        "username": "analista3",
        "nombre": "Analista de Sala 3",
        "password_hash": hash_password("Sala2026*"),
        "rol": "ANALISTA",
        "activo": True,
        "fecha_creacion": "2026-11-12 08:00:00",
        "ultimo_acceso": "2026-11-12 16:20:00"
    },
    # 5 Usuarios Ejecutivos
    {
        "username": "gobernador",
        "nombre": "Despacho del Gobernador",
        "password_hash": hash_password("Portuguesa2026"),
        "rol": "EJECUTIVO",
        "activo": True,
        "fecha_creacion": "2026-11-12 08:00:00",
        "ultimo_acceso": "2026-11-12 22:10:00"
    },
    {
        "username": "jefepceo",
        "nombre": "Jefe del Puesto de Comando",
        "password_hash": hash_password("Comando2026"),
        "rol": "EJECUTIVO",
        "activo": True,
        "fecha_creacion": "2026-11-12 08:00:00",
        "ultimo_acceso": "2026-11-12 20:05:00"
    },
    {
        "username": "asistente1",
        "nombre": "Asistente Ejecutivo 1",
        "password_hash": hash_password("Ejecutivo2026"),
        "rol": "EJECUTIVO",
        "activo": True,
        "fecha_creacion": "2026-11-12 08:00:00",
        "ultimo_acceso": "2026-11-12 14:30:00"
    },
    {
        "username": "asistente2",
        "nombre": "Asistente Ejecutivo 2",
        "password_hash": hash_password("Ejecutivo2026"),
        "rol": "EJECUTIVO",
        "activo": True,
        "fecha_creacion": "2026-11-12 08:00:00",
        "ultimo_acceso": "2026-11-11 17:00:00"
    },
    {
        "username": "asistente3",
        "nombre": "Asistente Ejecutivo 3",
        "password_hash": hash_password("Ejecutivo2026"),
        "rol": "EJECUTIVO",
        "activo": True,
        "fecha_creacion": "2026-11-12 08:00:00",
        "ultimo_acceso": "2026-11-10 11:45:00"
    }
]

DEFAULT_AUDITORIA = [
    {
        "id": "AUD-001",
        "timestamp": "2026-11-12 21:30:15",
        "username": "master1",
        "nombre": "Manuel Hidalgo — Coordinación PCEO",
        "modulo": "Fiesta del Agua",
        "accion": "Cambio de Estatus Operativo",
        "detalle": "Pozo PZ-GUA-01 (Guanare) actualizado a OPERATIVO (SI). Motivo: Sustitución de motor 50HP."
    },
    {
        "id": "AUD-002",
        "timestamp": "2026-11-12 22:15:40",
        "username": "analista1",
        "nombre": "Analista de Sala 1",
        "modulo": "Plan Cero Botes",
        "accion": "Registro de Reparación",
        "detalle": "Reparación de bote en Páez, Comunidad Centro. Caudal: 1.50 L/s (129.600 Lts/Día). Caso 1x10: SI."
    },
    {
        "id": "AUD-003",
        "timestamp": "2026-11-12 23:05:10",
        "username": "analista2",
        "nombre": "Analista de Sala 2",
        "modulo": "Tramos Caídos",
        "accion": "Actualización de Tramo",
        "detalle": "Tramo en Guanare / Parroquia Guanare / Barrio San Antonio actualizado a Ejecutado (100%)."
    },
    {
        "id": "AUD-004",
        "timestamp": "2026-11-12 23:40:22",
        "username": "master1",
        "nombre": "Manuel Hidalgo — Coordinación PCEO",
        "modulo": "Ruta del Hidrojet",
        "accion": "Registro de Jornada",
        "detalle": "Jornada en Araure / Urb. Baraure 4. Colector: 280 m liberados, 4 bocas de visita, 220 beneficiarios."
    }
]

class AuthManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AuthManager, cls).__new__(cls)
            cls._instance._init_manager()
        return cls._instance

    def _init_manager(self):
        self._ensure_files()
        self.users: List[Dict] = self._load_users()
        self.auditoria: List[Dict] = self._load_auditoria()

    def _ensure_files(self):
        """Crea automáticamente los archivos de usuarios y auditoría si no existen."""
        if not os.path.exists(USUARIOS_JSON_PATH):
            with open(USUARIOS_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_USERS, f, indent=2, ensure_ascii=False)

        if not os.path.exists(AUDITORIA_JSON_PATH):
            with open(AUDITORIA_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_AUDITORIA, f, indent=2, ensure_ascii=False)

    def _load_users(self) -> List[Dict]:
        try:
            with open(USUARIOS_JSON_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error cargando usuarios: {e}")
            return list(DEFAULT_USERS)

    def _save_users(self):
        try:
            with open(USUARIOS_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(self.users, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando usuarios: {e}")

    def _load_auditoria(self) -> List[Dict]:
        try:
            with open(AUDITORIA_JSON_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error cargando auditoría: {e}")
            return list(DEFAULT_AUDITORIA)

    def _save_auditoria(self):
        try:
            with open(AUDITORIA_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(self.auditoria, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando auditoría: {e}")

    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[Dict], str]:
        """
        Valida las credenciales del usuario.
        Retorna (éxito, user_dict, mensaje_error).
        """
        if not username or not password:
            return False, None, "Por favor ingrese su usuario y contraseña."

        uname = username.strip().lower()
        user = next((u for u in self.users if u["username"].lower() == uname), None)

        if not user:
            return False, None, "El usuario ingresado no existe en el sistema."

        if not user.get("activo", True):
            return False, None, "Cuenta desactivada por la Coordinación Master. Contacte al administrador."

        hashed = hash_password(password.strip())
        if user.get("password_hash") != hashed:
            return False, None, "Contraseña incorrecta. Verifique sus credenciales."

        # Actualizar último acceso
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user["ultimo_acceso"] = now_str
        self._save_users()

        return True, user, "Acceso concedido."

    def get_users(self) -> List[Dict]:
        return list(self.users)

    def get_user(self, username: str) -> Optional[Dict]:
        uname = username.strip().lower()
        return next((u for u in self.users if u["username"].lower() == uname), None)

    def create_user(
        self,
        username: str,
        nombre: str,
        password: str,
        rol: str,
        creator_username: str = "master1"
    ) -> Tuple[bool, str]:
        """Crea una nueva cuenta de usuario."""
        uname = username.strip().lower()
        if not uname:
            return False, "El nombre de usuario es obligatorio."
        if not nombre.strip():
            return False, "El nombre completo es obligatorio."
        if not password.strip():
            return False, "La contraseña es obligatoria."
        if rol not in ("MASTER", "ANALISTA", "EJECUTIVO"):
            return False, "El rol seleccionado no es válido."

        if any(u["username"].lower() == uname for u in self.users):
            return False, f"El usuario '@{uname}' ya se encuentra registrado."

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_u = {
            "username": uname,
            "nombre": nombre.strip(),
            "password_hash": hash_password(password.strip()),
            "rol": rol,
            "activo": True,
            "fecha_creacion": now_str,
            "ultimo_acceso": "Nunca"
        }
        self.users.append(new_u)
        self._save_users()

        # Registrar en auditoría
        self.log_audit(
            username=creator_username,
            nombre=self.get_user(creator_username).get("nombre", "Master") if self.get_user(creator_username) else "Master",
            modulo="Gestión de Usuarios",
            accion="Creación de Usuario",
            detalle=f"Se creó la cuenta '@{uname}' ({nombre.strip()}) con rol {rol}."
        )

        return True, f"Usuario '@{uname}' creado exitosamente."

    def update_user(
        self,
        username: str,
        nombre: Optional[str] = None,
        rol: Optional[str] = None,
        activo: Optional[bool] = None,
        editor_username: str = "master1"
    ) -> Tuple[bool, str]:
        """Actualiza datos de un usuario existente."""
        user = self.get_user(username)
        if not user:
            return False, f"Usuario '@{username}' no encontrado."

        cambios = []
        if nombre is not None and nombre.strip() and nombre.strip() != user.get("nombre"):
            cambios.append(f"Nombre: '{user.get('nombre')}' -> '{nombre.strip()}'")
            user["nombre"] = nombre.strip()

        if rol is not None and rol in ("MASTER", "ANALISTA", "EJECUTIVO") and rol != user.get("rol"):
            cambios.append(f"Rol: '{user.get('rol')}' -> '{rol}'")
            user["rol"] = rol

        if activo is not None and activo != user.get("activo"):
            estado_txt = "ACTIVADA" if activo else "DESACTIVADA"
            cambios.append(f"Estado: {estado_txt}")
            user["activo"] = activo

        if not cambios:
            return True, "No se registraron cambios."

        self._save_users()

        # Auditoría
        self.log_audit(
            username=editor_username,
            nombre=self.get_user(editor_username).get("nombre", "Master") if self.get_user(editor_username) else "Master",
            modulo="Gestión de Usuarios",
            accion="Modificación de Usuario",
            detalle=f"Actualización de '@{username}': {'; '.join(cambios)}."
        )

        return True, f"Usuario '@{username}' actualizado correctamente."

    def reset_password(
        self,
        username: str,
        new_password: str,
        master_username: str = "master1"
    ) -> Tuple[bool, str]:
        """Restablece la contraseña de un usuario."""
        user = self.get_user(username)
        if not user:
            return False, f"Usuario '@{username}' no encontrado."
        if not new_password or len(new_password.strip()) < 4:
            return False, "La nueva contraseña debe tener al menos 4 caracteres."

        user["password_hash"] = hash_password(new_password.strip())
        self._save_users()

        self.log_audit(
            username=master_username,
            nombre=self.get_user(master_username).get("nombre", "Master") if self.get_user(master_username) else "Master",
            modulo="Gestión de Usuarios",
            accion="Restablecimiento de Contraseña",
            detalle=f"Se restableció la contraseña de la cuenta '@{username}'."
        )

        return True, f"Contraseña de '@{username}' restablecida exitosamente."

    def toggle_user_active(self, username: str, master_username: str = "master1") -> Tuple[bool, str]:
        """Alterna el estado activo/inactivo de un usuario."""
        user = self.get_user(username)
        if not user:
            return False, "Usuario no encontrado."
        
        # Evitar desactivar todos los masters
        if user["rol"] == "MASTER" and user.get("activo", True):
            active_masters = sum(1 for u in self.users if u["rol"] == "MASTER" and u.get("activo", True))
            if active_masters <= 1:
                return False, "No es posible desactivar la única cuenta Master activa del sistema."

        new_status = not user.get("activo", True)
        return self.update_user(username, activo=new_status, editor_username=master_username)

    def log_audit(
        self,
        username: str,
        nombre: str,
        modulo: str,
        accion: str,
        detalle: str
    ):
        """Registra un evento en la bitácora de auditoría."""
        next_id = f"AUD-{len(self.auditoria) + 1:04d}"
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "id": next_id,
            "timestamp": now_str,
            "username": username,
            "nombre": nombre,
            "modulo": modulo,
            "accion": accion,
            "detalle": detalle
        }
        self.auditoria.insert(0, entry) # El más reciente arriba
        self._save_auditoria()

    def get_auditoria(self) -> List[Dict]:
        return list(self.auditoria)
