"""
Test TrueFoundry LLM Integration

This script tests the TrueFoundry OpenAI-compatible endpoint.
"""
import os
import sys

# Set TrueFoundry configuration
os.environ['LLM_PROVIDER'] = 'truefoundry'
os.environ['LLM_API_KEY'] = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Im9YWU5yQmV0d2pEZDI3emZvZkk0ZHUyVGVybyJ9.eyJhdWQiOiI3MDYxNzk3NC02ZDNhLTYzMzYtMzMzNi0zMjMzMzUzMjYyNjMiLCJleHAiOjM3MjM3ODcwNjgsImlhdCI6MTc2NDIzNTA2OCwiaXNzIjoidHJ1ZWZvdW5kcnkuY29tIiwic3ViIjoiY21paDgwYTVqMDA3djAxbmU0ZjhpMjBpNSIsImp0aSI6ImNtaWg4MGE1cjAwODAwMW5lMGFuMWdyZTIiLCJzdWJqZWN0U2x1ZyI6ImNkcC1wcm9kdWN0IiwidXNlcm5hbWUiOiJjZHAtcHJvZHVjdCIsInVzZXJUeXBlIjoic2VydmljZWFjY291bnQiLCJzdWJqZWN0VHlwZSI6InNlcnZpY2VhY2NvdW50IiwidGVuYW50TmFtZSI6InBheXRtIiwicm9sZXMiOltdLCJqd3RJZCI6ImNtaWg4MGE1cjAwODAwMW5lMGFuMWdyZTIiLCJhcHBsaWNhdGlvbklkIjoiNzA2MTc5NzQtNmQzYS02MzM2LTMzMzYtMzIzMzM1MzI2MjYzIn0.F-1Yt1D1qP9JrK8O0mDulnKQ1BolKYBDyCpu_Ao5TsJtqRA8v0fZxnpbHG41e147DBAg56LzVqkqrX5R6Y3smHW5uCdTW0_5l1fsLTlAMTIlVRgiEIEk6StCWw9smvQK5YZd80TYppbsOqB4w9E01zJdmtU2FNpS5GcAtJvD5aN_y61c4zdtbIiTmFxPQwyUJ7FLj-EXIL8QBTLt4Z-uR2QOc_PvaGSNH0hBy6ylU_RHLTrPHjKDPPGcaiy4rtO9em60mqeRsy8l-bqt5PqGd1J5trtkFepU5ac4WHXCkfu8-LRb0O4KZrIc--GCHUmdfhFFVpynR2SoeWZase5EUA'
os.environ['LLM_MODEL'] = 'pi-agentic/us-anthropic-claude-sonnet-4-20250514-v1-0'
os.environ['LLM_BASE_URL'] = 'https://tfy.internal.ap-south-1.production.apps.pai.mypaytm.com/api/llm/api/inference/openai'

print("=" * 60)
print("Testing TrueFoundry LLM Integration")
print("=" * 60)

# Test 1: Direct OpenAI client call
print("\n[Test 1] Direct OpenAI client call...")
try:
    from openai import OpenAI
    
    client = OpenAI(
        api_key=os.environ['LLM_API_KEY'],
        base_url=os.environ['LLM_BASE_URL']
    )
    
    response = client.chat.completions.create(
        model=os.environ['LLM_MODEL'],
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'TrueFoundry connection successful!' in exactly those words."}
        ],
        max_tokens=50
    )
    
    print(f"  ✅ Response: {response.choices[0].message.content}")
    print("  ✅ Direct OpenAI client: SUCCESS")
except Exception as e:
    print(f"  ❌ Direct OpenAI client: FAILED - {e}")
    sys.exit(1)

# Test 2: DSPy integration
print("\n[Test 2] DSPy integration...")
try:
    import dspy
    from llm_provider import configure_dspy_from_env, get_dspy_lm, LLMConfig
    
    # Show configuration
    config = LLMConfig.from_env()
    print(f"  Provider: {config.provider.value}")
    print(f"  Model: {config.model}")
    print(f"  Base URL: {config.base_url}")
    
    # Configure DSPy
    configure_dspy_from_env()
    lm = get_dspy_lm()
    
    print(f"  ✅ DSPy LM initialized: {type(lm).__name__}")
    print("  ✅ DSPy integration: SUCCESS")
except Exception as e:
    print(f"  ❌ DSPy integration: FAILED - {e}")
    import traceback
    traceback.print_exc()

# Test 3: Simple DSPy signature
print("\n[Test 3] DSPy Signature test...")
try:
    class SimpleSignature(dspy.Signature):
        """Answer questions concisely."""
        question: str = dspy.InputField()
        answer: str = dspy.OutputField()
    
    predictor = dspy.Predict(SimpleSignature)
    result = predictor(question="What is 2 + 2?")
    
    print(f"  ✅ Question: What is 2 + 2?")
    print(f"  ✅ Answer: {result.answer}")
    print("  ✅ DSPy Signature: SUCCESS")
except Exception as e:
    print(f"  ❌ DSPy Signature: FAILED - {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)


