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

### 🕒 Scheduling with Cron (Optional)

This project can be run on a schedule using a `cron` job. A template file `crontab.txt` is provided in the root of the project.

1.  **Review the template**: Open `crontab.txt` and ensure the paths to the project directory and the `pipenv` executable are correct for your system.
2.  **Install the cron job**: Run the following command from the project root to add the job to your system's crontab without deleting existing jobs:
    ```bash
    (crontab -l 2>/dev/null; cat crontab.txt) | crontab -
    ```
3.  **Verify**: You can check that the job was installed correctly by running `crontab -l`.

Logs for the scheduled runs will be redirected to `/tmp/social_content_automation.log`.

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
