---
name: context-builder
description: Construct compact, factual, clean context text from database records for prompt engineering, stripping unnecessary fields and preventing data manipulation.
---
# Context Builder Skill

## Objective
Convert raw database records into a clean, concise, structured text format specifically optimized for LLM comprehension and factual grounding.

## Inputs
- List of tour records returned by `tour_retriever`.

## Outputs
- Clean, compact text block representing the available tour options.

## Rules
- Do NOT add information not present in the database.
- Do NOT alter prices, discounts, or seat counts.
- Do NOT invent fake hotels, flights, or policies.
- Format prices in clear Vietnamese currency format (e.g. `3.200.000 VNĐ`).
- Include essential fields only: Tour Title, Destination, Duration, Price, Next Departure Date, Available Seats, Highlights.
- If list is empty, output an explicit indicator: `[KHÔNG TÌM THẤY TOUR NÀO THỎA MÃN TRONG CSDL]`.

