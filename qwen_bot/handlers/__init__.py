from aiogram import Router
from .cancel import router as cancel_router  # ← Сначала cancel!
from .start_cmd import router as start_cmd_router  # ← добавили
from .help_cmd import router as help_cmd_router  # ← новая строка
from .student import router as student_router
from .exam import router as exam_router
from .materials import router as materials_router
from .assistant import router as assistant_router
from .workspace import router as workspace_router
from .payment import router as payment_router

main_router = Router()

main_router.include_router(cancel_router)
main_router.include_router(start_cmd_router)  # ← подключаем до student
main_router.include_router(help_cmd_router)  # ← новая строка
main_router.include_router(student_router)
main_router.include_router(exam_router)
main_router.include_router(materials_router)
main_router.include_router(assistant_router)
main_router.include_router(workspace_router)
main_router.include_router(payment_router)