# Анализ YouTube-канала @Vedensky ("ОСНОВА")

Анализ YouTube-канала **[@Vedensky](https://www.youtube.com/@Vedensky)** — "ОСНОВА" на выборке из **232 видео**, собранных через YouTube Data API v3.  
Включает в себя ETL-пайплайн, очистку данных, анализ временных рядов и корреляционный анализ.

## Стек технологий

- **Python 3.14**
- **Pandas** (Data manipulation)
- **Matplotlib / Seaborn** (Data visualization)
- **Requests** (API interaction)
- **Cloudflare Workers** (Bypassing regional restrictions for YouTube API)

## Запуск проекта

**1. Клонируйте репозиторий:**

```bash
git clone https://github.com/Arctiqa/YTchAnalytics-vedensky.git
cd YTchAnalytics-vedensky
```

**2. Установите зависимости:**

```bash
poetry install
```

**3. Добавьте ключ YouTube API в `.env`:**

```env
YT_API_KEY=your_api_key_here
```

**4. Запустите скрипт сбора данных (ETL):**

```bash
python -m src.export_data
```

**5. Откройте Jupyter Notebook для анализа:**

```bash
jupyter notebook
```
