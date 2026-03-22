# 🎥 Система управления потоковым вещанием

![Python](https://img.shields.io/badge/python-3.12%2B-blue) ![Django](https://img.shields.io/badge/django-5.2-green) ![Channels](https://img.shields.io/badge/channels-4.3-red) ![License](https://img.shields.io/badge/license-MIT-yellow)

**Система управления потоковым вещанием** — это полноценная веб-платформа для организации аудио и видео трансляций с ролевой системой пользователей. Проект позволяет ведущим проводить прямые эфиры с использованием WebRTC, управлять плейлистами, а слушателям — подключаться к трансляциям и общаться с ведущими в реальном времени.

---

## 📋 Содержание

- [🎯 О проекте](#-о-проекте)
- [✨ Основные возможности](#-основные-возможности)
- [🏗 Архитектура](#-архитектура)
- [🛠 Технологический стек](#-технологический-стек)
- [📋 Требования](#-требования)
- [🚀 Установка и запуск](#-установка-и-запуск)
- [🔧 Конфигурация](#-конфигурация)
- [👥 Ролевая модель](#-ролевая-модель)
- [📱 Интерфейс пользователя](#-интерфейс-пользователя)
- [🔌 API Endpoints](#-api-endpoints)
- [🌐 WebSocket События](#-websocket-события)
- [🗄 Структура базы данных](#-структура-базы-данных)
- [🐳 Docker](#-docker)
- [📝 Логирование](#-логирование)
- [🔧 Устранение неисправностей](#-устранение-неисправностей)

---

## 🎯 О проекте

Система управления потоковым вещанием разработана для организации прямых эфиров в закрытых группах. Проект идеально подходит для:

- 🎙 **Онлайн-радиостанций** — ведущие могут транслировать музыку из плейлистов
- 🎥 **Видеостриминга** — прямые эфиры с камерой и микрофоном через WebRTC
- 🎧 **Корпоративных трансляций** — внутренние мероприятия и презентации
- 🎵 **Музыкальных клубов** — обмен аудиоматериалами и совместное прослушивание

### Ключевые особенности

| Особенность | Описание |
|-------------|----------|
| 🔐 **Ролевая система** | Администратор, ведущий, слушатель — у каждого свои права |
| 📹 **WebRTC трансляции** | Прямые эфиры с низкой задержкой без дополнительных плагинов |
| 📀 **Медиатека** | Загрузка аудио и видео файлов с автоматическим определением длительности |
| 🎵 **Плейлисты** | Создание, редактирование, drag&drop сортировка |
| 🎙 **Запись аудио** | Запись голосовых сообщений прямо в браузере |
| 💬 **Чат с ведущим** | Обмен сообщениями в реальном времени |
| 🛡 **Мягкое удаление** | Пользователи и файлы не удаляются физически, а маркируются |
| 🎨 **Jazzmin админка** | Стильная админ-панель с кастомизацией |

---

## ✨ Основные возможности

### 👤 Для слушателей

- Просмотр списка активных трансляций
- Подключение к аудио/видео эфиру через WebRTC
- Регулировка громкости
- Отправка текстовых и голосовых сообщений ведущему
- Отображение информации о текущем треке

### 🎙 Для ведущих

- **Управление эфиром:**
  - Включение/выключение микрофона
  - Включение/выключение камеры
  - Настройка громкости
  - Выбор фонового плейлиста

- **Медиатека:**
  - Загрузка аудио (MP3, WAV, OGG, WebM) до 50 МБ
  - Загрузка видео (MP4, WebM) до 500 МБ
  - Просмотр и удаление файлов
  - Массовое выделение и удаление

- **Плейлисты:**
  - Создание и переименование
  - Добавление файлов из медиатеки
  - Drag&drop сортировка треков
  - Настройка зацикливания и перемешивания
  - Воспроизведение в эфире

- **Запись аудио:**
  - Запись через микрофон прямо в браузере
  - Автоматическое определение длительности
  - Сохранение в медиатеку с возможностью добавления в плейлист

- **Сообщения:**
  - Просмотр сообщений от слушателей
  - Изменение статуса (новое/в работе/завершено)
  - Архивация обработанных сообщений

### 👨‍💼 Для администраторов

- **Управление пользователями:**
  - Просмотр всех пользователей с фильтрацией (логин, ФИО, роль, дата регистрации)
  - Редактирование логина и ФИО
  - Смена пароля
  - Назначение ролей (пользователь/ведущий/администратор)
  - Мягкое удаление пользователей

---

## 🏗 Архитектура

Проект построен на модульной архитектуре с четким разделением ответственности:

```
┌─────────────────────────────────────────────────────────────────┐
│                         Клиент (Browser)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  HTTP/HTTPS │  │  WebSocket  │  │      WebRTC (P2P)       │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Django + Channels                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    ASGI Application                        │  │
│  │  ┌─────────────┐  ┌─────────────────────────────────────┐ │  │
│  │  │   HTTP      │  │           WebSocket                 │ │  │
│  │  │  (WSGI)     │  │  ┌─────────────────────────────┐   │ │  │
│  │  └─────────────┘  │  │   BroadcastConsumer         │   │ │  │
│  │                   │  │   (для ведущих)             │   │ │  │
│  │                   │  └─────────────────────────────┘   │ │  │
│  │                   │  ┌─────────────────────────────┐   │ │  │
│  │                   │  │   StreamConsumer            │   │ │  │
│  │                   │  │   (для слушателей)          │   │ │  │
│  │                   │  └─────────────────────────────┘   │ │  │
│  │                   └─────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                         PostgreSQL                               │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  auth_user │ media_files │ playlists │ broadcasts │ messages │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Компоненты системы

| Компонент | Описание |
|-----------|----------|
| **Django** | Основной фреймворк, обработка HTTP запросов, ORM, админка |
| **Django Channels** | Поддержка WebSocket для реального времени |
| **WebRTC** | P2P передача видео/аудио между ведущим и слушателями |
| **Jazzmin** | Стильная админ-панель с кастомизацией |
| **PostgreSQL** | Основная база данных |

---

## 🛠 Технологический стек

### Backend

| Технология | Версия | Назначение |
|------------|--------|------------|
| Python | 3.12+ | Язык программирования |
| Django | 5.2.12 | Веб-фреймворк |
| Django Channels | 4.3.2 | WebSocket поддержка |
| PostgreSQL | latest | База данных |
| psycopg2-binary | 2.9.11 | Драйвер PostgreSQL |
| django-jazzmin | 3.0.4 | Админ-панель |
| gunicorn | 25.1.0 | WSGI сервер |
| python-dotenv | 1.2.2 | Управление переменными окружения |

### Frontend

| Технология | Назначение |
|------------|------------|
| HTML5/CSS3 | Структура и стили |
| JavaScript (ES6+) | Интерактивность |
| WebRTC API | Видео/аудио трансляции |
| MediaRecorder API | Запись аудио |
| Fetch API | HTTP запросы |
| WebSocket API | Realtime сообщения |

---

## 📋 Требования

### Программное обеспечение

- **Python** 3.12 или выше
- **PostgreSQL** 14 или выше
- **Git** (для клонирования репозитория)
- **Docker** (опционально, для контейнеризации)

### Браузер

Для корректной работы WebRTC и записи аудио требуется:

- **Chrome/Edge** 90+
- **Firefox** 88+
- **Safari** 15+ (ограниченная поддержка WebRTC)

---

## 🚀 Установка и запуск

### Способ 1: Локальная установка

#### 1. Клонирование репозитория

```bash
git clone https://sourcecraft.dev/hackathons-team/ttk-streaming
cd ttk-streaming
```

#### 2. Создание виртуального окружения

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

#### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

#### 4. Настройка базы данных

Создайте базу данных PostgreSQL:

```sql
CREATE DATABASE streaming_db;
CREATE USER streaming_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE streaming_db TO streaming_user;
```

#### 5. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
# Django
SECRET_KEY=your-secret-key-here

# Database
DB_NAME=streaming_db
DB_USER=streaming_user
DB_PASSWORD=your_password
DB_PORT=5432
```

#### 6. Применение миграций

```bash
python manage.py migrate
```

#### 7. Создание суперпользователя

```bash
python manage.py createsuperuser
```

#### 8. Сбор статических файлов

```bash
python manage.py collectstatic
```

#### 9. Запуск сервера

```bash
python manage.py runserver
```

Приложение будет доступно по адресу: http://localhost:8000

---

### Способ 2: Docker Compose

#### 1. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
SECRET_KEY=your-secret-key-here
DB_NAME=streaming_db
DB_USER=streaming_user
DB_PASSWORD=your_password
DB_PORT=5432
```

#### 2. Запуск контейнеров

```bash
docker-compose up -d
```

#### 3. Применение миграций

```bash
docker-compose exec web python manage.py migrate
```

#### 4. Создание суперпользователя

```bash
docker-compose exec web python manage.py createsuperuser
```

---

## 🔧 Конфигурация

### Основные настройки (settings.py)

| Параметр | Значение по умолчанию | Описание |
|----------|----------------------|----------|
| `DEBUG` | True | Режим отладки (отключить в production) |
| `ALLOWED_HOSTS` | localhost, 127.0.0.1, 0.0.0.0 | Разрешенные хосты |
| `AUTH_USER_MODEL` | accounts.User | Кастомная модель пользователя |
| `CHANNEL_LAYERS` | InMemoryChannelLayer | Каналы для WebSocket |

### Кастомные настройки

```python
# Размеры загружаемых файлов
DATA_UPLOAD_MAX_MEMORY_SIZE = 1000 * 1024 * 1024  # 1 ГБ

# Пути для статики и медиа
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
```

---

## 👥 Ролевая модель

### Роли и права доступа

| Действие | Пользователь | Ведущий | Администратор |
|----------|--------------|---------|---------------|
| Просмотр трансляций | ✅ | ✅ | ✅ |
| Подключение к эфиру | ✅ | ✅ | ✅ |
| Отправка сообщений | ✅ | ✅ | ✅ |
| Проведение эфира | ❌ | ✅ | ✅ |
| Управление медиатекой | ❌ | ✅ | ✅ |
| Управление плейлистами | ❌ | ✅ | ✅ |
| Админ-панель | ❌ | ❌ | ✅ |
| Управление пользователями | ❌ | ❌ | ✅ |

### Модель User (accounts/models.py)

```python
class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('leader', 'Ведущий'),
        ('admin', 'Администратор'),
    ]
    
    full_name = models.CharField(max_length=255)  # ФИО (только кириллица)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    is_deleted = models.BooleanField(default=False)  # Мягкое удаление
    deleted_at = models.DateTimeField(null=True, blank=True)
```

---

## 📱 Интерфейс пользователя

### Структура страниц

```
/myttk_streaming/accounts/login/     → Страница входа
/myttk_streaming/accounts/register/  → Страница регистрации
/myttk_streaming/player/             → Плеер для слушателей
/myttk_streaming/host/               → Панель ведущего
/myttk_streaming/admin_panel/        → Админ-панель (только админ)
```

### Навигация

```
┌─────────────────────────────────────────────────────────────────┐
│  [Лого]  │  Администрирование  │  Плеер  │  Раздел ведущего    │  [👤 Имя] │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔌 API Endpoints

### Аутентификация (accounts)

| Метод | URL | Описание |
|-------|-----|----------|
| GET/POST | `/accounts/login/` | Авторизация |
| GET/POST | `/accounts/register/` | Регистрация |
| GET | `/accounts/logout/` | Выход |

### Администрирование (player)

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/users/` | Получение списка пользователей |
| POST | `/api/users/<id>/edit/` | Редактирование пользователя |
| DELETE | `/api/users/<id>/delete/` | Удаление пользователя |
| POST | `/api/users/<id>/change-password/` | Смена пароля |
| POST | `/api/users/<id>/assign-role/` | Назначение роли |

### Медиатека

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/media-files/` | Получение списка файлов |
| POST | `/api/media-files/upload/` | Загрузка файла |
| DELETE | `/api/media-files/<id>/delete/` | Удаление файла |

### Плейлисты

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/playlists/` | Список плейлистов |
| POST | `/api/playlists/create/` | Создание плейлиста |
| GET | `/api/playlists/<id>/` | Элементы плейлиста |
| PUT | `/api/playlists/<id>/rename/` | Переименование |
| DELETE | `/api/playlists/<id>/delete/` | Удаление плейлиста |
| POST | `/api/playlists/<id>/add/` | Добавление файла |
| DELETE | `/api/playlists/<id>/remove/<item_id>/` | Удаление из плейлиста |
| POST | `/api/playlists/<id>/reorder/` | Сортировка |
| POST | `/api/playlists/<id>/toggle-setting/` | Настройка (loop/shuffle) |

### Трансляции

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/broadcasts/active/` | Активные трансляции |
| POST | `/api/broadcast/start/` | Начать трансляцию |
| POST | `/api/broadcast/stop/` | Остановить трансляцию |
| GET | `/api/broadcast/status/` | Статус трансляции |
| POST | `/api/broadcast/volume/` | Изменить громкость |

### Аудиозаписи

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/api/recordings/upload/` | Загрузка аудиозаписи |
| GET | `/api/recordings/` | Список записей |
| DELETE | `/api/recordings/<id>/delete/` | Удаление записи |

### Сообщения

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/messages/` | Список сообщений |
| POST | `/api/messages/<id>/status/` | Изменить статус |

---

## 🌐 WebSocket События

### BroadcastConsumer (для ведущих)

**Подключение:** `ws://host/ws/broadcast/`

| Событие (action) | Данные | Описание |
|------------------|--------|----------|
| `start_broadcast` | `{playlist_id, volume, cam_enabled}` | Начать трансляцию |
| `stop_broadcast` | `{}` | Остановить трансляцию |
| `toggle_mic` | `{enabled}` | Вкл/Выкл микрофон |
| `toggle_cam` | `{enabled}` | Вкл/Выкл камеру |
| `set_volume` | `{volume}` | Изменить громкость |
| `webrtc_offer` | `{offer, listener_id}` | WebRTC offer |
| `webrtc_answer` | `{answer, listener_id}` | WebRTC answer |

### StreamConsumer (для слушателей)

**Подключение:** `ws://host/ws/stream/`

| Событие (action) | Данные | Описание |
|------------------|--------|----------|
| `join_stream` | `{user_id}` | Подключиться к трансляции |
| `leave_stream` | `{}` | Покинуть трансляцию |
| `send_message` | `{message}` | Отправить сообщение |
| `webrtc_answer` | `{answer, broadcaster_id}` | WebRTC answer |

---

## 🗄 Структура базы данных

### Основные таблицы

```sql
-- Пользователи (accounts_user)
auth_user
├── id (PK)
├── username (уникальный, латиница)
├── full_name (кириллица)
├── role (user/leader/admin)
├── is_deleted (мягкое удаление)
├── deleted_at
└── date_joined

-- Медиафайлы (player_mediafile)
player_mediafile
├── id (PK)
├── user_id (FK → auth_user)
├── title
├── file (путь)
├── media_type (audio/video)
├── duration
├── uploaded_at
└── is_deleted

-- Плейлисты (player_playlist)
player_playlist
├── id (PK)
├── user_id (FK → auth_user)
├── name
├── created_at
├── is_active
├── loop
├── shuffle
└── is_playing

-- Элементы плейлиста (player_playlistitem)
player_playlistitem
├── id (PK)
├── playlist_id (FK → player_playlist)
├── media_file_id (FK → player_mediafile)
└── order

-- Трансляции (player_broadcast)
player_broadcast
├── id (PK)
├── user_id (FK → auth_user)
├── playlist_id (FK → player_playlist, nullable)
├── is_active
├── volume
├── mic_enabled
├── cam_enabled
├── started_at
└── ended_at

-- Сообщения (player_message)
player_message
├── id (PK)
├── user_id (FK → auth_user)
├── content
├── status (new/in_progress/completed)
├── created_at
└── updated_at

-- Аудиозаписи (player_audiorecording)
player_audiorecording
├── id (PK)
├── user_id (FK → auth_user)
├── title
├── audio_file
├── duration
├── created_at
└── added_to_playlist
```

---

## 🐳 Docker

### Структура docker-compose.yml

```yaml
services:
  db:
    image: postgres:latest
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgres://${DB_USER}:${DB_PASSWORD}@db/${DB_NAME}
```

### Полезные команды Docker

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f web

# Выполнение команд Django
docker-compose exec web python manage.py migrate

# Остановка сервисов
docker-compose down

# Остановка с удалением томов
docker-compose down -v
```

---

## 📝 Логирование

Система использует модуль `logging` Python для отслеживания работы:

```python
import logging
logger = logging.getLogger(__name__)

# Формат логов
# %(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### Уровни логирования

| Уровень | Использование |
|---------|---------------|
| `INFO` | Подключения WebSocket, запуск трансляций |
| `WARNING` | Проблемы с доступом, превышение лимитов |
| `ERROR` | Ошибки подключения, исключения |

---

## 🔧 Устранение неисправностей

### Проблема: WebSocket не подключается

**Решение:**
1. Проверьте, что запущен ASGI сервер: `python manage.py runserver`
2. Убедитесь, что `ASGI_APPLICATION` настроен в settings.py
3. Проверьте маршруты в `routing.py`

### Проблема: Не загружаются файлы

**Решение:**
1. Проверьте размер файла (аудио ≤ 50 МБ, видео ≤ 500 МБ)
2. Убедитесь, что формат поддерживается (MP3, WAV, OGG, WebM для аудио; MP4, WebM для видео)
3. Проверьте права на запись в папке `media/`

### Проблема: WebRTC не работает

**Решение:**
1. Убедитесь, что сайт открыт по HTTPS или localhost (WebRTC требует secure context)
2. Проверьте разрешения на доступ к камере и микрофону в браузере
3. Убедитесь, что STUN серверы доступны

### Проблема: Не сохраняется сессия

**Решение:**
1. Проверьте настройки `SESSION_ENGINE` в settings.py
2. Убедитесь, что `SECRET_KEY` установлен в .env
3. Проверьте, что файлы cookies не блокируются браузером

### Проблема: Не работает запись аудио

**Решение:**
1. Убедитесь, что браузер поддерживает MediaRecorder API
2. Разрешите доступ к микрофону
3. Проверьте консоль браузера на ошибки JavaScript

---