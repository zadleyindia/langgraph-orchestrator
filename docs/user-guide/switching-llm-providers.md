# Switching LLM Providers

This guide explains how to switch between different LLM providers (OpenAI, Anthropic, Google AI) in the LangGraph Orchestrator.

## Available Providers

- **OpenAI**: GPT-4, GPT-4 Turbo, GPT-3.5 Turbo
- **Anthropic**: Claude-3 Opus, Claude-3 Sonnet  
- **Google AI**: Gemini Pro, Gemini Pro Vision

## Method 1: Environment Variables (Recommended)

Edit your `.env` file:

```bash
# Set the provider
LLM_PROVIDER=anthropic

# Set the model
LLM_MODEL=claude-3-sonnet-20240229

# Optional: Set temperature
LLM_TEMPERATURE=0.1
```

### Provider Options:
- `openai` - Uses OpenAI models
- `anthropic` - Uses Anthropic Claude models
- `google` - Uses Google AI models

### Model Options by Provider:

**OpenAI:**
- `gpt-4`
- `gpt-4-turbo`
- `gpt-3.5-turbo`

**Anthropic:**
- `claude-3-opus-20240229`
- `claude-3-sonnet-20240229`

**Google AI:**
- `gemini-pro`
- `gemini-pro-vision`

## Method 2: Programmatic Switching

```python
from orchestrator.llm import switch_provider

# Switch to Anthropic Claude
switch_provider("anthropic", "claude-3-opus-20240229")

# Switch to OpenAI GPT-4
switch_provider("openai", "gpt-4")

# Switch to Google Gemini
switch_provider("google", "gemini-pro")
```

## Required API Keys

Make sure you have the appropriate API keys in your `.env` file:

```bash
# OpenAI
OPENAI_API_KEY=sk-proj-your-openai-key-here

# Anthropic
ANTHROPIC_API_KEY=sk-ant-api03-your-anthropic-key-here

# Google AI
GOOGLE_API_KEY=your-google-ai-key-here
```

## Agent-Specific Temperatures

Each agent type has optimized temperature settings:

- **Personal Assistant**: 0.1 (consistent responses)
- **Data Analyst**: 0.0 (deterministic)  
- **HR Director**: 0.3 (some creativity)
- **Dev Lead**: 0.2 (mostly consistent)
- **Operations Manager**: 0.1 (consistent)

You can override these by setting `LLM_TEMPERATURE` in your `.env` file.

## Checking Available Providers

```python
from orchestrator.llm import get_available_providers

providers = get_available_providers()
print(providers)
```

## Restart Required

After changing environment variables, restart the orchestrator for changes to take effect:

```bash
# If running in development
python -m orchestrator.main

# Or restart your service
```

## Troubleshooting

### Missing API Key Error
- Ensure the API key for your chosen provider is set in `.env`
- Check that the key is valid and has sufficient credits

### Module Not Found Error
- Install the required dependencies:
  ```bash
  pip install langchain-openai langchain-anthropic langchain-google-genai
  ```

### Invalid Model Error
- Verify the model name matches the supported models list above
- Check provider documentation for latest model names