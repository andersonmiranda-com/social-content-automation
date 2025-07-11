# Social Media Content Automation

This project automates the process of generating and publishing content to social media platforms like Instagram and LinkedIn. It uses various APIs to fetch data, generate content, and post it.

---

## 🚀 Setup and Installation

Follow these steps to get the project running on your local machine.

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd social-linkedin-instagram
    ```

2.  **Install dependencies:**
    This project uses `pipenv` to manage dependencies. Make sure you have it installed (`pip install pipenv`). Then, run the following command to install all required packages for production and development:

    ```bash
    pipenv install --dev
    ```

3.  **Activate the virtual environment:**
    To work within the project's isolated environment, run:
    ```bash
    pipenv shell
    ```

---

## ⚙️ Configuration

The project requires API keys and other secrets to connect to external services.

1.  **Create a `.env` file:**
    It is recommended to copy the `.env.example` file (if it exists) or create a new `.env` file manually.

    ```bash
    cp .env.example .env
    ```

2.  **Fill in the variables:**
    Open the `.env` file and add the necessary environment variables. The specific keys will depend on the services you use.

    **Example:**

    ```dotenv
    # .env
    # Credentials for external services
    OPENAI_API_KEY="sk-..."
    CLOUDINARY_URL="cloudinary://api_key:api_secret@cloud_name"
    LINKEDIN_ACCESS_TOKEN="..."
    ```

---

## ▶️ Usage

The main entry point for running automation flows is `main.py`.

_Instructions on how to execute specific flows will be added here once they are implemented._
