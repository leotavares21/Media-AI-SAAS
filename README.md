

# MediaSense 🚀

O **MediaSense** é uma plataforma inteligente para upload, transcrição e análise automática de arquivos de áudio e vídeo. O sistema utiliza processamento assíncrono para transcrever arquivos de mídia e extrair *insights* acionáveis (resumos, sentimento geral e tópicos relevantes) através de modelos de Inteligência Artificial via **Groq Cloud API**.

---

https://github.com/user-attachments/assets/703bba20-f9fe-4b95-a722-34bd315bece7



## 🛠️ Tecnologias Utilizadas

| Camada | Tecnologia | Descrição |
| :--- | :--- | :--- |
| **Frontend** | **Next.js 14+** | Interface moderna com suporte a Server/Client Components e Tailwind CSS. |
| **Backend** | **FastAPI** | API REST rápida e assíncrona em Python. |
| **Task Queue** | **Celery & Redis** | Processamento assíncrono de mídia em segundo plano e Pub/Sub para SSE. |
| **Banco de Dados** | **PostgreSQL** | Armazenamento de dados relacionais e histórico de processamento. |
| **Migrações** | **Alembic** | Controle de versão e migrações da estrutura do banco de dados. |
| **Storage** | **MinIO** | Object Storage compatível com S3 para armazenamento dos arquivos de mídia. |
| **IA / LLM** | **Groq Cloud API** | Análise de texto, sentimento e tópicos utilizando `openai/gpt-oss-120b`. |
| **Transcrição** | **Whisper** | Conversão de áudio/vídeo em texto. |

---

## ⚡ Principais Funcionalidades

* **Upload Interativo:** Suporte a arquivos de áudio e vídeo (`MP3`, `WAV`, `MP4`, etc.) de até 500MB com zona interativa de *Drag & Drop*.
* **Transcrição de Mídia:** Conversão automática de áudio em texto formatado.
* **Extração de Insights via IA:**
  * **Resumo executivo:** Síntese curta do conteúdo falado.
  * **Análise de Sentimento:** Classificação estrita (*Positivo*, *Neutro* ou *Negativo*).
  * **Tópicos Relevantes:** Mapeamento dinâmico de palavras-chave e temas abordados.
* **Notificações em Tempo Real:** Acompanhamento do progresso do processamento no frontend via **SSE (Server-Sent Events)** alimentado por Redis.

---

## 🏗️ Arquitetura e Fluxo do Sistema

1. **Upload:** O usuário envia a mídia pela interface Next.js.
2. **Armazenamento:** O FastAPI recebe o arquivo e o salva no bucket do **MinIO**.
3. **Fila de Tarefas:** Um *Job* é registrado no **PostgreSQL** e enviado para a fila do **Celery** via **Redis**.
4. **Transcrição e IA:** O worker do Celery processa a transcrição com Whisper e envia o texto para a **Groq Cloud API** para extrair os *insights*.
5. **Notificação SSE:** Conforme o progresso é atualizado (0% a 100%), o Redis dispara eventos para o frontend via streaming.

---

## 📂 Estrutura das Variáveis de Ambiente (`.env`)

Crie um arquivo `.env` na raiz do diretório `backend`:

```env
# Configurações do Banco de Dados
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mediasense

# Redis & Celery
REDIS_URL=redis://localhost:6379/0

# MinIO Storage
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=media-files

# Integração Groq Cloud AI
GROQ_API_KEY=gsk_sua_chave_groq_aqui
