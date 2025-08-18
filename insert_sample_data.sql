INSERT INTO users (username, email, password_hash) VALUES
    ('samantha', 'samantha@example.com', 'hash123'),
    ('john', 'john@example.com', 'hash456');

INSERT INTO contacts (user_id, contact_name, contact_email, contact_phone) VALUES
    (1, 'John Doe', 'john@example.com', '123-456-7890'),
    (2, 'Samantha Smith', 'samantha@example.com', '098-765-4321');

INSERT INTO messages (sender_id, receiver_id, content) VALUES
    (1, 2, 'Hi Samantha, how can we collaborate on The Third Voice?'),
    (2, 1, 'Hey John, let’s discuss the AI features!');

INSERT INTO ai_response_cache (message_id, ai_response) VALUES
    (1, 'This message shows interest in collaboration. Suggested reply: Discuss project goals and timelines.'),
    (2, 'This message is about AI features. Suggested reply: Share specific AI requirements.');
