CREATE DATABASE IF NOT EXISTS nexchat;
USE nexchat;

DROP TABLE IF EXISTS reactions;
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS room_members;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS friends;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    nexchat_id    VARCHAR(20) UNIQUE NOT NULL,
    username      VARCHAR(80) UNIQUE NOT NULL,
    email         VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    avatar        VARCHAR(10) DEFAULT '👤',
    photo         VARCHAR(255) DEFAULT NULL,
    bio           VARCHAR(200) DEFAULT '',
    status        VARCHAR(20) DEFAULT 'online',
    theme         VARCHAR(10) DEFAULT 'dark',
    is_online     BOOLEAN DEFAULT FALSE,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE friends (
    user_id   INT NOT NULL,
    friend_id INT NOT NULL,
    PRIMARY KEY (user_id, friend_id),
    FOREIGN KEY (user_id)   REFERENCES users(id),
    FOREIGN KEY (friend_id) REFERENCES users(id)
);

CREATE TABLE rooms (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(255) DEFAULT '',
    is_private  BOOLEAN DEFAULT FALSE,
    created_by  INT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE room_members (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    room_id   INT NOT NULL,
    user_id   INT NOT NULL,
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE messages (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    sender_id       INT NOT NULL,
    room_name       VARCHAR(100) NOT NULL,
    content         TEXT NOT NULL,
    msg_type        VARCHAR(20) DEFAULT 'text',
    disappear_after INT DEFAULT 0,
    seen_at         DATETIME DEFAULT NULL,
    is_deleted      BOOLEAN DEFAULT FALSE,
    timestamp       DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(id)
);

CREATE TABLE reactions (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    message_id INT NOT NULL,
    user_id    INT NOT NULL,
    emoji      VARCHAR(10) NOT NULL,
    UNIQUE KEY unique_reaction (message_id, user_id),
    FOREIGN KEY (message_id) REFERENCES messages(id),
    FOREIGN KEY (user_id)    REFERENCES users(id)
);

INSERT IGNORE INTO rooms (name, description, is_private) VALUES
('general', 'General chat for everyone', FALSE),
('random',  'Random topics', FALSE),
('tech',    'Tech discussions', FALSE);

SELECT 'NexChat database setup complete!' AS status;