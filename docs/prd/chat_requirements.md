# Chat Module Requirements

## 1. Overview
The Chat Module enables private 1-on-1 messaging and communication securely between Helpers and Hosts (or any two platform users).

## 2. Key Functional Requirements

### 2.1. Conversational History
- Support initiating and listing 1-on-1 conversations between two registered users.
- Track the latest message interaction timestamp to order and sort active conversations in an inbox view.
- Ensure that only one unique conversation exists between any two specific participants.

### 2.2. Messaging
- Users can send text messages within their active conversations.
- Messages must be securely tied to the user sending them (Sender).
- Support tracking of read receipts. Messages must record when the recipient has read them.
- Retrieve conversation history ordered chronologically.

## 3. Non-Functional Requirements
- Efficient storage and retrieval leveraging explicit indexing on participants and message timestamps.
