# 🚀 Social Content Automation – LangChain API Backend

Social media content automation (text + image + publishing) using a **pure LangChain + LangServe** architecture.

Modular. Scalable. Flexible. Designed as an alternative to platforms like n8n, but with clean, decoupled code.

---

## 🧩 Lego-like Modular Architecture

- Each **Chain** performs a task (generate text, image, format, validate).
- **Pipelines** compose multiple chains to create a complete flow.
- All logic is orchestrated with `RunnableSequence`, `RunnableMap`, etc.
- The configuration for each block lives in `config/*.yaml`.

---

## 📁 Project Structure

```

langserve\_app/
├── chains/             # Small reusable functions (text, image, upload)
├── pipelines/          # Flows that combine multiple chains
├── tools/              # External connectors (Canva, Cloudinary, Sheets…)
├── config/             # Configuration YAMLs
├── app.py              # FastAPI + LangServe API
modules/                # Reused modules (LLM, storage, social, etc.)
tests/                  # Unit tests per chain/pipeline

````

---

## ▶️ Local Execution (with LangServe)

1. Clone and enter the project:

```bash
git clone https://github.com/andersonmiranda-com/social-content-automation
cd social-content-automation
````

2. Install dependencies:

```bash
pipenv install --dev
pipenv shell
```

3. Create your `.env` file:

```bash
cp langserve_app/.env.example langserve_app/.env
```

4. Run the LangServe server:

```bash
uvicorn langserve_app.app:app --reload
```

---

## 🧪 How to Test Chains

Each Chain has a web playground at:

```
http://localhost:8000/<path>/playground
```

And you can also POST to:

```
POST /<path>/invoke
```

Example:

```
POST /generate/invoke
{
  "topic": "gratitude",
  "type": "REEL"
}
```

---

## ⚙️ Customization

Each chain uses its YAML configuration in `langserve_app/config/`.

You can edit:

* Prompt templates
* Generation parameters
* Destination folder in Cloudinary
* Canva templates

Without modifying the source code.

---

## 🧪 Testing and Linting

```bash
pytest
black .
mypy .
```

---

## 📌 Roadmap (next steps)

* [x] Complete migration to LangChain + LangServe
* [ ] Scheduler configuration (`cron`)
* [ ] Canva API integration
* [ ] Visual dashboard (Streamlit or Next.js)
* [ ] Automatic publishing webhook

---

## 🧠 Philosophy

> Think of chains as pure functions.
> Think of pipelines as flows.
> And may everything be replaceable like Lego pieces.

---

## 🧑‍💻 Author

Anderson Miranda – [@andersonmiranda\_com](https://github.com/andersonmiranda-com)

---

## License

MIT
