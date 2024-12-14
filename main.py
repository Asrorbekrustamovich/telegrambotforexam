from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from Database import create_table, get_kurs_info, insert_kurs
from aiogram.filters import StateFilter
import asyncio
from dotenv import load_dotenv
import os
load_dotenv()
TOKEN=os.getenv('TOKEN')

bot = Bot(token=TOKEN)
ADMIN_ID = os.getenv("ADMIN_ID")
dp = Dispatcher()


# States class
class AdminStates(StatesGroup):
    kurs_nomi = State() 
    kurs_narxi = State()  
    kurs_malumoti = State()  
    kurs_oqituvchisi = State() 


def UMUmiy(user_id):
    kbs = [
        [types.KeyboardButton(text="o`quv kurslar")],
        [types.KeyboardButton(text="bizning afzalliklarimiz")]
    ]
    if user_id == ADMIN_ID:
        kbs.append([types.KeyboardButton(text="kurs qoshish")])

    return types.ReplyKeyboardMarkup(keyboard=kbs, resize_keyboard=True)


def inline_kurslar():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="Backend", callback_data="kurs_backend"),
        types.InlineKeyboardButton(text="Frontend", callback_data="kurs_frontend")
    )
    return builder.as_markup()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        text=f"Assalomu aleykum, hurmatli {message.from_user.first_name}, "
             f"bu bot bizning kurslarimiz haqida ma'lumot beradi!",
        reply_markup=UMUmiy(message.from_user.id)
    )


@dp.message(lambda message: message.text == "bizning afzalliklarimiz")
async def go_to_main_menu(message: Message, state: FSMContext):
     await message.answer(
            """
        Soff Study – bu zamonaviy va sifatli o‘quv markazidir,
        unga kirish orqali talabalar texnologiya, biznes, va turli sohalarda bilim olish imkoniyatiga ega bo‘lishadi.
        O‘quv markazi o‘zining tajribali o‘qituvchilari va innovatsion ta'lim metodikalari bilan tanilgan.
        Soff Study o‘z o‘quvchilariga amaliy bilim va ko‘nikmalarni berishga intiladi, shu bilan birga, ularning kelajakda muvaffaqiyatli kasbiy faoliyat olib borishlarini ta'minlashga qaratilgan. 
            """
        )
@dp.message(lambda message: message.text == "kurs qoshish")
async def go_to_main_menu(message: Message, state: FSMContext):
            if message.from_user.id==ADMIN_ID:
                await message.answer("Kurs qo'shish uchun quyidagi ma'lumotlarni kiriting:")
                await message.answer("Kurs nomini kiriting:")
                await state.set_state(AdminStates.kurs_nomi) 


@dp.message(StateFilter(AdminStates.kurs_nomi))  # Fixed: directly using AdminStates.kurs_nomi
async def process_kurs_nomi(message: Message, state: FSMContext):
    kurs_nomi = message.text
    print(kurs_nomi)
    await state.update_data(kurs_nomi=kurs_nomi)
    await message.answer("Kurs narxini kiriting:")
    print(message.text)
    await state.set_state(AdminStates.kurs_narxi)  # Transition to kurs_narxi


@dp.message( StateFilter(AdminStates.kurs_narxi))  
async def process_kurs_narxi(message: Message, state: FSMContext):
    kurs_narxi = message.text
    await state.update_data(kurs_narxi=kurs_narxi)
    await message.answer("Kurs haqida to'liq ma'lumot kiriting:")
    await state.set_state(AdminStates.kurs_malumoti) 


@dp.message(StateFilter(AdminStates.kurs_malumoti))  
async def process_kurs_malumoti(message: Message, state: FSMContext):
    kurs_malumoti = message.text
    await state.update_data(kurs_malumoti=kurs_malumoti)
    await message.answer("Kurs o'qituvchisini kiriting:")
    await state.set_state(AdminStates.kurs_oqituvchisi)  # Transition to kurs_oqituvchisi


@dp.message(StateFilter(AdminStates.kurs_oqituvchisi))  # Fixed: directly using AdminStates.kurs_oqituvchisi
async def process_kurs_oqituvchisi(message: Message, state: FSMContext):
    kurs_oqituvchisi = message.text
    await state.update_data(kurs_oqituvchisi=kurs_oqituvchisi)
    user_data = await state.get_data()
    kurs_nomi = user_data['kurs_nomi']
    kurs_narxi = user_data['kurs_narxi']
    kurs_malumoti = user_data['kurs_malumoti']
    kurs_oqituvchisi = user_data['kurs_oqituvchisi']
    insert_kurs(kurs_nomi, kurs_narxi, kurs_malumoti, kurs_oqituvchisi)
    await message.answer(f"Yangi kurs ma'lumotlari:\n\n"
                         f"Kurs nomi: {kurs_nomi}\n"
                         f"Kurs narxi: {kurs_narxi}\n"
                         f"To'liq ma'lumot: {kurs_malumoti}\n"
                         f"O'qituvchi: {kurs_oqituvchisi}\n")

    await state.clear()
@dp.message(lambda message: message.text == "o`quv kurslar")
async def show_courses(message: Message):
    await message.answer(
        text="Quyidagi kurslardan birini tanlang:",
        reply_markup=inline_kurslar()
    )

@dp.callback_query()
async def handle_callback(callback: CallbackQuery):
    if callback.data == "kurs_backend":
        info = get_kurs_info("Backend")
        if isinstance(info, str):  # If "Mavjud emas" is returned
            await callback.message.answer("Backend kursi haqida ma'lumot topilmadi.")
        elif isinstance(info, tuple):  # Single row
            kurs_narxi, toliq_malumot, kurs_oqituvchisi = info
            await callback.message.answer(
                text=f"Backend kursi\n\n"
                     f"Narxi: {kurs_narxi}\n"
                     f"Ma'lumot: {toliq_malumot}\n"
                     f"O'qituvchi: {kurs_oqituvchisi}"
            )
        elif isinstance(info, list):  # Multiple rows
            for kurs in info:
                kurs_narxi, toliq_malumot, kurs_oqituvchisi = kurs
                await callback.message.answer(
                    text=f"Backend kursi\n\n"
                         f"Narxi: {kurs_narxi}\n"
                         f"Ma'lumot: {toliq_malumot}\n"
                         f"O'qituvchi: {kurs_oqituvchisi}"
                )

    elif callback.data == "kurs_frontend":
        info = get_kurs_info("Frontend")
        if isinstance(info, str):  # If "Mavjud emas" is returned
            await callback.message.answer("Frontend kursi haqida ma'lumot topilmadi.")
        elif isinstance(info, tuple):  # Single row
            kurs_narxi, toliq_malumot, kurs_oqituvchisi = info
            await callback.message.answer(
                text=f"Frontend kursi\n\n"
                     f"Narxi: {kurs_narxi}\n"
                     f"Ma'lumot: {toliq_malumot}\n"
                     f"O'qituvchi: {kurs_oqituvchisi}"
            )
        elif isinstance(info, list):  # Multiple rows
            for kurs in info:
                kurs_narxi, toliq_malumot, kurs_oqituvchisi = kurs
                await callback.message.answer(
                    text=f"Frontend kursi\n\n"
                         f"Narxi: {kurs_narxi}\n"
                         f"Ma'lumot: {toliq_malumot}\n"
                         f"O'qituvchi: {kurs_oqituvchisi}"
                )


async def main():
    create_table()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
