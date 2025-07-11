# Social Media Content Automation

## 🧩 Philosophy & Modular Architecture

This project is inspired by visual automation platforms like n8n, but here workflows are built with code. The key is modularity and reusability: each feature or integration is implemented as an independent module, designed to be reused and combined in different flows, just like Lego bricks.

- **Workflows**: Defined in the `flows/` folder, orchestrating automation logic by combining modules.
- **Modules**: Each integration or feature lives in `modules/` and must be decoupled and reusable.
- **Utilities**: Helper code in `utils/` for cross-cutting concerns.

### For Developers

When contributing, design every new feature as a modular and reusable block. Always think about how your code can be combined in different flows and avoid unnecessary dependencies between modules.

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
