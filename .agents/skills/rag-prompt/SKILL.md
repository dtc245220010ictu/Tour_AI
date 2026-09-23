---
name: rag-prompt
description: Construct robust, grounded system and user prompts that enforce strict zero-hallucination policies and professional Vietnamese tone for travel consultation.
---
# RAG Prompt Engineering Skill

## Objective
Assemble prompt components into a bulletproof template that guides the AI model to provide accurate, polite, and persuasive tour consultations strictly bound to retrieved context.

## Structure
System Role
    ↓
Grounding Rules (Zero-hallucination constraint)
    ↓
Context (Factual data from CSDL)
    ↓
User Question
    ↓
Response Formatting Guidelines

## Rules
- Explicitly instruct the model: "CHỈ sử dụng thông tin trong mục CONTEXT. Tuyệt đối không tự suy diễn hoặc bịa đặt tour/giá tiền".
- Instruct model to state politely when no tours match.
- Instruct model to answer in natural, courteous Vietnamese.
- Forbid answering general questions unrelated to the tour catalog when consulting products.

