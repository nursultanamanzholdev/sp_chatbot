# Chat and Lecture Mode Implementation

This document outlines the changes made to implement chat/lecture mode selection in the application.

## Database Changes

1. Added a `mode` column to the `prompts` table with a default value of 'chat'
   ```sql
   ALTER TABLE prompts 
   ADD COLUMN IF NOT EXISTS mode VARCHAR(20) DEFAULT 'chat';
   ```

2. Updated the `Prompt` model in `models.py` to include the mode field:
   ```python
   mode = Column(String, default="chat")
   ```

## Backend Changes

1. Updated `schemas.py` to include the mode field in:
   - PromptBase
   - PromptCreate
   - Prompt
   - PromptUpdate

2. Updated API endpoints in `main.py` to handle the mode field:
   - `/api/prompts` POST endpoint (create_prompt)
   - `/api/prompts/{prompt_id}` PUT endpoint (update_prompt)

## Frontend Changes

1. Updated the API client in `api.ts` to include the mode field in:
   - createPrompt
   - updatePrompt

2. Updated `AddUserModal.tsx` component to:
   - Add a RadioGroup for selecting between chat and lecture modes
   - Pass the selected mode to the onAddUser callback

3. Updated `dashboard/page.tsx` to:
   - Update the handleAddUser function to include the mode parameter
   - Update the EditPromptDialog to include mode selection
   - Display the selected mode in the prompt card

## How to Use

1. Run the database migration to add the mode column:
   ```
   psql -U your_username -d your_database_name -f alter_prompts_table.sql
   ```
   or use the migrations.py file that's been updated

2. When creating a new prompt, users can now select between "Chat Mode" and "Lecture Mode"

3. When editing a prompt, users can change the mode

4. The selected mode is displayed in the prompt card on the dashboard

## Implementation Details

- **Chat Mode**: The default interactive mode where content is presented in a back-and-forth dialogue format
- **Lecture Mode**: A more structured format where content is presented as a comprehensive lecture 