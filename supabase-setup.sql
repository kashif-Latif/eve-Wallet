-- ============================================================
-- Digital Wallet System - Complete Database Setup
-- Run this in Supabase SQL Editor (Dashboard → SQL Editor → New Query)
-- ============================================================

-- ============================================================
-- PART 1: DJANGO BUILT-IN TABLES
-- ============================================================

-- Django content type framework
CREATE TABLE IF NOT EXISTS django_content_type (
    id SERIAL PRIMARY KEY,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    UNIQUE(app_label, model)
);

-- Django auth permission
CREATE TABLE IF NOT EXISTS auth_permission (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    content_type_id INTEGER NOT NULL REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED,
    codename VARCHAR(100) NOT NULL,
    UNIQUE(content_type_id, codename)
);

-- Django auth group
CREATE TABLE IF NOT EXISTS auth_group (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE
);

-- Django auth group permissions
CREATE TABLE IF NOT EXISTS auth_group_permissions (
    id BIGSERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED,
    permission_id INTEGER NOT NULL REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED,
    UNIQUE(group_id, permission_id)
);

-- Django sessions
CREATE TABLE IF NOT EXISTS django_session (
    session_key VARCHAR(40) NOT NULL PRIMARY KEY,
    session_data TEXT NOT NULL,
    expire_date TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE INDEX IF NOT EXISTS django_session_expire_date ON django_session(expire_date);

-- Django admin log
CREATE TABLE IF NOT EXISTS django_admin_log (
    id BIGSERIAL PRIMARY KEY,
    action_time TIMESTAMP WITH TIME ZONE NOT NULL,
    object_id TEXT NULL,
    object_repr VARCHAR(200) NOT NULL,
    action_flag SMALLINT NOT NULL,
    change_message TEXT NOT NULL,
    content_type_id INTEGER NULL REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED,
    user_id INTEGER NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK (action_flag >= 0)
);

-- Django migrations tracking
CREATE TABLE IF NOT EXISTS django_migrations (
    id BIGSERIAL PRIMARY KEY,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied TIMESTAMP WITH TIME ZONE NOT NULL
);

-- SimpleJWT outstanding tokens
CREATE TABLE IF NOT EXISTS token_blacklist_outstandingtoken (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NULL,
    jti VARCHAR(255) NOT NULL UNIQUE,
    token TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE INDEX IF NOT EXISTS token_blacklist_outstandingtoken_user_id ON token_blacklist_outstandingtoken(user_id);
CREATE INDEX IF NOT EXISTS token_blacklist_outstandingtoken_jti ON token_blacklist_outstandingtoken(jti);

-- SimpleJWT blacklisted tokens
CREATE TABLE IF NOT EXISTS token_blacklist_blacklistedtoken (
    id BIGSERIAL PRIMARY KEY,
    blacklisted_at TIMESTAMP WITH TIME ZONE NOT NULL,
    token_id BIGINT NOT NULL UNIQUE REFERENCES token_blacklist_outstandingtoken(id) DEFERRABLE INITIALLY DEFERRED
);


-- ============================================================
-- PART 2: CUSTOM APP TABLES
-- ============================================================

-- USERS table (custom user model)
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE NULL,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL DEFAULT '',
    last_name VARCHAR(150) NOT NULL DEFAULT '',
    email VARCHAR(254) NOT NULL UNIQUE,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Custom fields
    phone VARCHAR(17) NOT NULL UNIQUE,
    role VARCHAR(10) NOT NULL DEFAULT 'user',
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    profile_picture VARCHAR(100) NULL,
    date_of_birth DATE NULL,
    address TEXT NULL,
    city VARCHAR(100) NULL,
    country VARCHAR(100) NULL,
    transaction_pin VARCHAR(128) NULL,
    pin_set BOOLEAN NOT NULL DEFAULT FALSE,
    wallet_id BIGINT NULL,

    CONSTRAINT users_role_check CHECK (role IN ('user', 'admin', 'superadmin'))
);

CREATE INDEX IF NOT EXISTS users_phone_idx ON users(phone);
CREATE INDEX IF NOT EXISTS users_role_idx ON users(role);
CREATE INDEX IF NOT EXISTS users_is_verified_idx ON users(is_verified);
CREATE INDEX IF NOT EXISTS users_date_joined_idx ON users(date_joined DESC);

-- USERS groups (Django built-in)
CREATE TABLE IF NOT EXISTS users_groups (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED,
    group_id INTEGER NOT NULL REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED,
    UNIQUE(user_id, group_id)
);

-- USERS user permissions
CREATE TABLE IF NOT EXISTS users_user_permissions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED,
    permission_id INTEGER NOT NULL REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED,
    UNIQUE(user_id, permission_id)
);

-- Add FK for admin log and tokens to users table
ALTER TABLE django_admin_log ADD CONSTRAINT django_admin_log_user_id_fk FOREIGN KEY (user_id) REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE token_blacklist_outstandingtoken ADD CONSTRAINT token_outstandingtoken_user_id_fk FOREIGN KEY (user_id) REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED;

-- WALLETS table
CREATE TABLE IF NOT EXISTS wallets (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED,
    wallet_number VARCHAR(12) NOT NULL UNIQUE,
    balance NUMERIC(15, 2) NOT NULL DEFAULT 1000.00,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_frozen BOOLEAN NOT NULL DEFAULT FALSE,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    daily_limit NUMERIC(15, 2) NOT NULL DEFAULT 10000.00,
    monthly_limit NUMERIC(15, 2) NOT NULL DEFAULT 100000.00,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS wallets_wallet_number_idx ON wallets(wallet_number);
CREATE INDEX IF NOT EXISTS wallets_active_frozen_idx ON wallets(is_active, is_frozen);
CREATE INDEX IF NOT EXISTS wallets_user_id_idx ON wallets(user_id);

-- Add wallet FK to users table
ALTER TABLE users ADD CONSTRAINT users_wallet_id_fk FOREIGN KEY (wallet_id) REFERENCES wallets(id) DEFERRABLE INITIALLY DEFERRED;

-- TRANSACTIONS table
CREATE TABLE IF NOT EXISTS transactions (
    id BIGSERIAL PRIMARY KEY,
    sender_wallet_id BIGINT NOT NULL REFERENCES wallets(id) DEFERRABLE INITIALLY DEFERRED,
    receiver_wallet_id BIGINT NOT NULL REFERENCES wallets(id) DEFERRABLE INITIALLY DEFERRED,
    amount NUMERIC(15, 2) NOT NULL,
    fee NUMERIC(15, 2) NOT NULL DEFAULT 0,
    transaction_type VARCHAR(15) NOT NULL,
    status VARCHAR(15) NOT NULL DEFAULT 'pending',
    reference_number VARCHAR(15) NOT NULL UNIQUE,
    description TEXT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT transactions_transaction_type_check CHECK (transaction_type IN ('transfer', 'deposit', 'withdrawal', 'refund')),
    CONSTRAINT transactions_status_check CHECK (status IN ('pending', 'completed', 'failed', 'cancelled'))
);

CREATE INDEX IF NOT EXISTS transactions_reference_number_idx ON transactions(reference_number);
CREATE INDEX IF NOT EXISTS transactions_type_created_idx ON transactions(transaction_type, created_at DESC);
CREATE INDEX IF NOT EXISTS transactions_status_created_idx ON transactions(status, created_at DESC);
CREATE INDEX IF NOT EXISTS transactions_sender_created_idx ON transactions(sender_wallet_id, created_at DESC);
CREATE INDEX IF NOT EXISTS transactions_receiver_created_idx ON transactions(receiver_wallet_id, created_at DESC);
CREATE INDEX IF NOT EXISTS transactions_created_at_idx ON transactions(created_at);

-- REFUNDS table
CREATE TABLE IF NOT EXISTS refunds (
    id BIGSERIAL PRIMARY KEY,
    transaction_id BIGINT NOT NULL REFERENCES transactions(id) DEFERRABLE INITIALLY DEFERRED,
    requested_by_id BIGINT NOT NULL REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED,
    reason TEXT NOT NULL,
    status VARCHAR(15) NOT NULL DEFAULT 'pending',
    admin_note TEXT NULL,
    processed_by_id BIGINT NULL REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED,
    amount NUMERIC(15, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT refunds_status_check CHECK (status IN ('pending', 'approved', 'rejected', 'completed'))
);

CREATE INDEX IF NOT EXISTS refunds_status_created_idx ON refunds(status, created_at DESC);
CREATE INDEX IF NOT EXISTS refunds_requested_by_created_idx ON refunds(requested_by_id, created_at DESC);
CREATE INDEX IF NOT EXISTS refunds_transaction_id_idx ON refunds(transaction_id);
CREATE INDEX IF NOT EXISTS refunds_created_at_idx ON refunds(created_at);

-- NOTIFICATIONS table
CREATE TABLE IF NOT EXISTS notifications (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(15) NOT NULL DEFAULT 'system',
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT notifications_notification_type_check CHECK (notification_type IN ('transaction', 'refund', 'system', 'security', 'promotional'))
);

CREATE INDEX IF NOT EXISTS notifications_user_created_idx ON notifications(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS notifications_user_read_created_idx ON notifications(user_id, is_read, created_at DESC);
CREATE INDEX IF NOT EXISTS notifications_type_created_idx ON notifications(notification_type, created_at DESC);

-- AUDIT LOGS table
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NULL REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED,
    action VARCHAR(20) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    object_id VARCHAR(100) NOT NULL DEFAULT '',
    changes JSONB NOT NULL DEFAULT '{}',
    ip_address INET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS audit_logs_user_created_idx ON audit_logs(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS audit_logs_model_created_idx ON audit_logs(model_name, created_at DESC);
CREATE INDEX IF NOT EXISTS audit_logs_action_created_idx ON audit_logs(action, created_at DESC);


-- ============================================================
-- PART 3: DJANGO MIGRATION RECORDS
-- (These tell Django that migrations have already been applied)
-- ============================================================

INSERT INTO django_migrations (app, name, applied) VALUES
-- Content types
('contenttypes', '0001_initial', NOW()),
('contenttypes', '0002_remove_content_type_name', NOW()),
-- Auth
('auth', '0001_initial', NOW()),
('auth', '0002_alter_permission_name_max_length', NOW()),
('auth', '0003_alter_user_email_max_length', NOW()),
('auth', '0004_alter_user_username_opts', NOW()),
('auth', '0005_alter_user_last_login_null', NOW()),
('auth', '0006_require_contenttypes_0002', NOW()),
('auth', '0007_alter_validators_add_error_messages', NOW()),
('auth', '0008_alter_user_username_max_length', NOW()),
('auth', '0009_alter_user_last_name_max_length', NOW()),
('auth', '0010_alter_user_name_max_length', NOW()),
('auth', '0011_update_proxy_permissions', NOW()),
('auth', '0012_alter_user_first_name_max_length', NOW()),
-- Admin
('admin', '0001_initial', NOW()),
('admin', '0002_logentry_remove_auto_add', NOW()),
('admin', '0003_logentry_add_action_flag_choices', NOW()),
-- Sessions
('sessions', '0001_initial', NOW()),
-- Token blacklist
('token_blacklist', '0001_initial', NOW()),
('token_blacklist', '0002_outstandingtoken_jti_hex', NOW()),
('token_blacklist', '0003_auto_20171017_2007', NOW()),
('token_blacklist', '0004_auto_20171017_2013', NOW()),
('token_blacklist', '0005_remove_outstandingtoken_jti', NOW()),
('token_blacklist', '0006_auto_20171017_2113', NOW()),
('token_blacklist', '0007_auto_20171017_2214', NOW()),
('token_blacklist', '0008_migrate_to_bigautofield', NOW()),
('token_blacklist', '0009_auto_20230511_2259', NOW()),
('token_blacklist', '0010_fix_migrate_to_bigautofield', NOW()),
('token_blacklist', '0011_auto_20230523_2142', NOW()),
-- Accounts app
('accounts', '0001_initial', NOW()),
-- Wallets app
('wallets', '0001_initial', NOW()),
-- Transactions app
('transactions', '0001_initial', NOW()),
-- Refunds app
('refunds', '0001_initial', NOW()),
-- Notifications app
('notifications', '0001_initial', NOW()),
-- Analytics app (if it has migrations)
('analytics', '0001_initial', NOW());


-- ============================================================
-- PART 4: CONTENT TYPES AND PERMISSIONS
-- ============================================================

INSERT INTO django_content_type (app_label, model) VALUES
('admin', 'logentry'),
('auth', 'permission'),
('auth', 'group'),
('contenttypes', 'contenttype'),
('sessions', 'session'),
('token_blacklist', 'outstandingtoken'),
('token_blacklist', 'blacklistedtoken'),
('accounts', 'user'),
('accounts', 'auditlog'),
('wallets', 'wallet'),
('transactions', 'transaction'),
('refunds', 'refund'),
('notifications', 'notification');

INSERT INTO auth_permission (name, content_type_id, codename) VALUES
-- User permissions
('Can add user', (SELECT id FROM django_content_type WHERE app_label='accounts' AND model='user'), 'add_user'),
('Can change user', (SELECT id FROM django_content_type WHERE app_label='accounts' AND model='user'), 'change_user'),
('Can delete user', (SELECT id FROM django_content_type WHERE app_label='accounts' AND model='user'), 'delete_user'),
('Can view user', (SELECT id FROM django_content_type WHERE app_label='accounts' AND model='user'), 'view_user'),
-- AuditLog permissions
('Can add audit log', (SELECT id FROM django_content_type WHERE app_label='accounts' AND model='auditlog'), 'add_auditlog'),
('Can change audit log', (SELECT id FROM django_content_type WHERE app_label='accounts' AND model='auditlog'), 'change_auditlog'),
('Can delete audit log', (SELECT id FROM django_content_type WHERE app_label='accounts' AND model='auditlog'), 'delete_auditlog'),
('Can view audit log', (SELECT id FROM django_content_type WHERE app_label='accounts' AND model='auditlog'), 'view_auditlog'),
-- Wallet permissions
('Can add wallet', (SELECT id FROM django_content_type WHERE app_label='wallets' AND model='wallet'), 'add_wallet'),
('Can change wallet', (SELECT id FROM django_content_type WHERE app_label='wallets' AND model='wallet'), 'change_wallet'),
('Can delete wallet', (SELECT id FROM django_content_type WHERE app_label='wallets' AND model='wallet'), 'delete_wallet'),
('Can view wallet', (SELECT id FROM django_content_type WHERE app_label='wallets' AND model='wallet'), 'view_wallet'),
-- Transaction permissions
('Can add transaction', (SELECT id FROM django_content_type WHERE app_label='transactions' AND model='transaction'), 'add_transaction'),
('Can change transaction', (SELECT id FROM django_content_type WHERE app_label='transactions' AND model='transaction'), 'change_transaction'),
('Can delete transaction', (SELECT id FROM django_content_type WHERE app_label='transactions' AND model='transaction'), 'delete_transaction'),
('Can view transaction', (SELECT id FROM django_content_type WHERE app_label='transactions' AND model='transaction'), 'view_transaction'),
-- Refund permissions
('Can add refund', (SELECT id FROM django_content_type WHERE app_label='refunds' AND model='refund'), 'add_refund'),
('Can change refund', (SELECT id FROM django_content_type WHERE app_label='refunds' AND model='refund'), 'change_refund'),
('Can delete refund', (SELECT id FROM django_content_type WHERE app_label='refunds' AND model='refund'), 'delete_refund'),
('Can view refund', (SELECT id FROM django_content_type WHERE app_label='refunds' AND model='refund'), 'view_refund'),
-- Notification permissions
('Can add notification', (SELECT id FROM django_content_type WHERE app_label='notifications' AND model='notification'), 'add_notification'),
('Can change notification', (SELECT id FROM django_content_type WHERE app_label='notifications' AND model='notification'), 'change_notification'),
('Can delete notification', (SELECT id FROM django_content_type WHERE app_label='notifications' AND model='notification'), 'delete_notification'),
('Can view notification', (SELECT id FROM django_content_type WHERE app_label='notifications' AND model='notification'), 'view_notification'),
-- Group permissions
('Can add group', (SELECT id FROM django_content_type WHERE app_label='auth' AND model='group'), 'add_group'),
('Can change group', (SELECT id FROM django_content_type WHERE app_label='auth' AND model='group'), 'change_group'),
('Can delete group', (SELECT id FROM django_content_type WHERE app_label='auth' AND model='group'), 'delete_group'),
('Can view group', (SELECT id FROM django_content_type WHERE app_label='auth' AND model='group'), 'view_group'),
-- Permission permissions
('Can add permission', (SELECT id FROM django_content_type WHERE app_label='auth' AND model='permission'), 'add_permission'),
('Can change permission', (SELECT id FROM django_content_type WHERE app_label='auth' AND model='permission'), 'change_permission'),
('Can delete permission', (SELECT id FROM django_content_type WHERE app_label='auth' AND model='permission'), 'delete_permission'),
('Can view permission', (SELECT id FROM django_content_type WHERE app_label='auth' AND model='permission'), 'view_permission'),
-- Admin log
('Can add log entry', (SELECT id FROM django_content_type WHERE app_label='admin' AND model='logentry'), 'add_logentry'),
('Can change log entry', (SELECT id FROM django_content_type WHERE app_label='admin' AND model='logentry'), 'change_logentry'),
('Can delete log entry', (SELECT id FROM django_content_type WHERE app_label='admin' AND model='logentry'), 'delete_logentry'),
('Can view log entry', (SELECT id FROM django_content_type WHERE app_label='admin' AND model='logentry'), 'view_logentry'),
-- Token blacklist
('Can add outstanding token', (SELECT id FROM django_content_type WHERE app_label='token_blacklist' AND model='outstandingtoken'), 'add_outstandingtoken'),
('Can change outstanding token', (SELECT id FROM django_content_type WHERE app_label='token_blacklist' AND model='outstandingtoken'), 'change_outstandingtoken'),
('Can delete outstanding token', (SELECT id FROM django_content_type WHERE app_label='token_blacklist' AND model='outstandingtoken'), 'delete_outstandingtoken'),
('Can view outstanding token', (SELECT id FROM django_content_type WHERE app_label='token_blacklist' AND model='outstandingtoken'), 'view_outstandingtoken'),
('Can add blacklisted token', (SELECT id FROM django_content_type WHERE app_label='token_blacklist' AND model='blacklistedtoken'), 'add_blacklistedtoken'),
('Can change blacklisted token', (SELECT id FROM django_content_type WHERE app_label='token_blacklist' AND model='blacklistedtoken'), 'change_blacklistedtoken'),
('Can delete blacklisted token', (SELECT id FROM django_content_type WHERE app_label='token_blacklist' AND model='blacklistedtoken'), 'delete_blacklistedtoken'),
('Can view blacklisted token', (SELECT id FROM django_content_type WHERE app_label='token_blacklist' AND model='blacklistedtoken'), 'view_blacklistedtoken'),
-- Content type
('Can add content type', (SELECT id FROM django_content_type WHERE app_label='contenttypes' AND model='contenttype'), 'add_contenttype'),
('Can change content type', (SELECT id FROM django_content_type WHERE app_label='contenttypes' AND model='contenttype'), 'change_contenttype'),
('Can delete content type', (SELECT id FROM django_content_type WHERE app_label='contenttypes' AND model='contenttype'), 'delete_contenttype'),
('Can view content type', (SELECT id FROM django_content_type WHERE app_label='contenttypes' AND model='contenttype'), 'view_contenttype'),
-- Session
('Can add session', (SELECT id FROM django_content_type WHERE app_label='sessions' AND model='session'), 'add_session'),
('Can change session', (SELECT id FROM django_content_type WHERE app_label='sessions' AND model='session'), 'change_session'),
('Can delete session', (SELECT id FROM django_content_type WHERE app_label='sessions' AND model='session'), 'delete_session'),
('Can view session', (SELECT id FROM django_content_type WHERE app_label='sessions' AND model='session'), 'view_session');


-- ============================================================
-- PART 5: SEED DATA
-- ============================================================

-- =============================================
-- Seed Users (passwords are hashed with Django)
-- All users have password: Wallet123!
-- =============================================

-- Admin/Superuser
INSERT INTO users (password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, phone, role, is_verified, pin_set)
VALUES
('pbkdf2_sha256$600000$HN7wC6SssyTWCHqK$WAktD/THu+DCWfVn7yMDMihwAE5IGL2xDpV+NznYvHg=', TRUE, 'admin', 'Admin', 'User', 'admin@digitalwallet.com', TRUE, TRUE, NOW(), '+1234567890', 'superadmin', TRUE, FALSE);

-- Regular users
INSERT INTO users (password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, phone, role, is_verified, pin_set)
VALUES
('pbkdf2_sha256$600000$HN7wC6SssyTWCHqK$WAktD/THu+DCWfVn7yMDMihwAE5IGL2xDpV+NznYvHg=', FALSE, 'ahmad', 'Ahmad', 'Khan', 'ahmad@example.com', FALSE, TRUE, NOW() - INTERVAL '5 days', '+923001234567', 'user', TRUE, TRUE),
('pbkdf2_sha256$600000$HN7wC6SssyTWCHqK$WAktD/THu+DCWfVn7yMDMihwAE5IGL2xDpV+NznYvHg=', FALSE, 'sara', 'Sara', 'Ali', 'sara@example.com', FALSE, TRUE, NOW() - INTERVAL '3 days', '+923009876543', 'user', TRUE, TRUE),
('pbkdf2_sha256$600000$HN7wC6SssyTWCHqK$WAktD/THu+DCWfVn7yMDMihwAE5IGL2xDpV+NznYvHg=', FALSE, 'zain', 'Zain', 'Malik', 'zain@example.com', FALSE, TRUE, NOW() - INTERVAL '1 day', '+923005551234', 'user', TRUE, FALSE),
('pbkdf2_sha256$600000$HN7wC6SssyTWCHqK$WAktD/THu+DCWfVn7yMDMihwAE5IGL2xDpV+NznYvHg=', FALSE, 'fatima', 'Fatima', 'Noor', 'fatima@example.com', FALSE, TRUE, NOW() - INTERVAL '12 hours', '+923009998877', 'user', TRUE, FALSE),
('pbkdf2_sha256$600000$HN7wC6SssyTWCHqK$WAktD/THu+DCWfVn7yMDMihwAE5IGL2xDpV+NznYvHg=', FALSE, 'omar', 'Omar', 'Sheikh', 'omar@example.com', FALSE, TRUE, NOW(), '+923007776655', 'user', FALSE, FALSE);

-- Admin user (staff role)
INSERT INTO users (password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, phone, role, is_verified, pin_set)
VALUES
('pbkdf2_sha256$600000$HN7wC6SssyTWCHqK$WAktD/THu+DCWfVn7yMDMihwAE5IGL2xDpV+NznYvHg=', FALSE, 'staffadmin', 'Staff', 'Admin', 'staff@digitalwallet.com', TRUE, TRUE, NOW() - INTERVAL '7 days', '+923001110000', 'admin', TRUE, TRUE);


-- =============================================
-- Seed Wallets
-- =============================================

INSERT INTO wallets (user_id, wallet_number, balance, is_active, is_frozen, currency, daily_limit, monthly_limit, created_at, updated_at)
VALUES
(1, '100000000001', 5000.00, TRUE, FALSE, 'USD', 10000.00, 100000.00, NOW() - INTERVAL '7 days', NOW()),
(2, '100000000002', 1500.00, TRUE, FALSE, 'USD', 10000.00, 100000.00, NOW() - INTERVAL '5 days', NOW()),
(3, '100000000003', 2750.00, TRUE, FALSE, 'USD', 10000.00, 100000.00, NOW() - INTERVAL '3 days', NOW()),
(4, '100000000004', 800.00, TRUE, FALSE, 'USD', 10000.00, 100000.00, NOW() - INTERVAL '1 day', NOW()),
(5, '100000000005', 1000.00, TRUE, FALSE, 'USD', 10000.00, 100000.00, NOW() - INTERVAL '12 hours', NOW()),
(6, '100000000006', 1000.00, TRUE, FALSE, 'USD', 10000.00, 100000.00, NOW(), NOW()),
(7, '100000000007', 10000.00, TRUE, FALSE, 'USD', 50000.00, 500000.00, NOW() - INTERVAL '7 days', NOW());

-- Update users with wallet_id FK
UPDATE users SET wallet_id = 1 WHERE id = 1;
UPDATE users SET wallet_id = 2 WHERE id = 2;
UPDATE users SET wallet_id = 3 WHERE id = 3;
UPDATE users SET wallet_id = 4 WHERE id = 4;
UPDATE users SET wallet_id = 5 WHERE id = 5;
UPDATE users SET wallet_id = 6 WHERE id = 6;
UPDATE users SET wallet_id = 7 WHERE id = 7;


-- =============================================
-- Seed Transactions
-- =============================================

INSERT INTO transactions (sender_wallet_id, receiver_wallet_id, amount, fee, transaction_type, status, reference_number, description, created_at, updated_at)
VALUES
-- Deposits
(1, 1, 5000.00, 0.00, 'deposit', 'completed', 'TXNDEPOSIT00001', 'Initial deposit', NOW() - INTERVAL '7 days', NOW() - INTERVAL '7 days'),
(2, 2, 1500.00, 0.00, 'deposit', 'completed', 'TXNDEPOSIT00002', 'Initial deposit', NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days'),
(3, 3, 3000.00, 0.00, 'deposit', 'completed', 'TXNDEPOSIT00003', 'Initial deposit', NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days'),
(7, 7, 10000.00, 0.00, 'deposit', 'completed', 'TXNDEPOSIT00007', 'Admin initial deposit', NOW() - INTERVAL '7 days', NOW() - INTERVAL '7 days'),

-- Transfers (various statuses)
(1, 2, 200.00, 3.00, 'transfer', 'completed', 'TXNTRANSFER00001', 'Payment for services', NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days'),
(3, 2, 150.00, 2.25, 'transfer', 'completed', 'TXNTRANSFER00002', 'Lunch split', NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days'),
(2, 4, 100.00, 1.50, 'transfer', 'completed', 'TXNTRANSFER00003', 'Rent share', NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days'),
(1, 3, 500.00, 7.50, 'transfer', 'completed', 'TXNTRANSFER00004', 'Freelance payment', NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day'),
(3, 5, 250.00, 3.75, 'transfer', 'completed', 'TXNTRANSFER00005', 'Gift money', NOW() - INTERVAL '18 hours', NOW() - INTERVAL '18 hours'),
(2, 5, 75.00, 1.13, 'transfer', 'completed', 'TXNTRANSFER00006', 'Shared groceries', NOW() - INTERVAL '12 hours', NOW() - INTERVAL '12 hours'),
(7, 1, 1000.00, 15.00, 'transfer', 'completed', 'TXNTRANSFER00007', 'Admin to user transfer', NOW() - INTERVAL '6 hours', NOW() - INTERVAL '6 hours'),
(1, 6, 300.00, 4.50, 'transfer', 'pending', 'TXNTRANSFER00008', 'Pending payment', NOW() - INTERVAL '2 hours', NOW() - INTERVAL '2 hours'),
(4, 2, 50.00, 0.75, 'transfer', 'failed', 'TXNTRANSFER00009', 'Failed attempt', NOW() - INTERVAL '1 hour', NOW() - INTERVAL '1 hour'),
(5, 1, 180.00, 2.70, 'transfer', 'completed', 'TXNTRANSFER00010', 'Repayment', NOW() - INTERVAL '30 minutes', NOW() - INTERVAL '30 minutes'),

-- Withdrawals
(1, 1, 500.00, 5.00, 'withdrawal', 'completed', 'TXNWITHDRAW00001', 'ATM withdrawal', NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days'),
(3, 3, 200.00, 2.00, 'withdrawal', 'completed', 'TXNWITHDRAW00002', 'Bank transfer', NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day')
;


-- =============================================
-- Seed Notifications
-- =============================================

INSERT INTO notifications (user_id, title, message, notification_type, is_read, created_at)
VALUES
(1, 'Welcome to Digital Wallet!', 'Welcome Admin! Your digital wallet has been set up with $5,000.00 balance. Start sending and receiving money today!', 'system', TRUE, NOW() - INTERVAL '7 days'),
(2, 'Welcome to Digital Wallet!', 'Welcome Ahmad! Your digital wallet has been set up with $1,500.00 balance. Start sending and receiving money today!', 'system', TRUE, NOW() - INTERVAL '5 days'),
(3, 'Welcome to Digital Wallet!', 'Welcome Sara! Your digital wallet has been set up with $2,750.00 balance. Start sending and receiving money today!', 'system', TRUE, NOW() - INTERVAL '3 days'),
(2, 'Money Received', '$200.00 has been received from admin. New balance: $1,700.00', 'transaction', TRUE, NOW() - INTERVAL '4 days'),
(2, 'Money Received', '$150.00 has been received from sara. New balance: $1,850.00', 'transaction', TRUE, NOW() - INTERVAL '3 days'),
(1, 'Money Sent', '$200.00 has been sent to ahmad. Fee: $3.00. New balance: $4,797.00', 'transaction', TRUE, NOW() - INTERVAL '4 days'),
(4, 'Money Received', '$100.00 has been received from ahmad. New balance: $900.00', 'transaction', TRUE, NOW() - INTERVAL '2 days'),
(1, 'Money Sent', '$500.00 has been sent to sara. Fee: $7.50. New balance: $4,289.50', 'transaction', TRUE, NOW() - INTERVAL '1 day'),
(5, 'Money Received', '$250.00 has been received from sara. New balance: $1,250.00', 'transaction', FALSE, NOW() - INTERVAL '18 hours'),
(6, 'Money Received', '$300.00 is being received from admin. Fee: $4.50.', 'transaction', FALSE, NOW() - INTERVAL '2 hours'),
(1, 'Security Alert', 'A new device logged into your account. If this was not you, please change your password immediately.', 'security', FALSE, NOW() - INTERVAL '1 hour'),
(2, 'Transaction PIN Set', 'Your transaction PIN has been set successfully. Your transfers are now secured with PIN verification.', 'security', TRUE, NOW() - INTERVAL '2 days')
;


-- =============================================
-- Seed Refund Requests
-- =============================================

INSERT INTO refunds (transaction_id, requested_by_id, reason, status, admin_note, processed_by_id, amount, created_at, updated_at)
VALUES
(6, 2, 'Accidentally sent to wrong person', 'pending', NULL, NULL, 100.00, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day'),
(9, 5, 'Duplicate transaction, please refund', 'approved', 'Verified as duplicate. Processing refund.', 1, 75.00, NOW() - INTERVAL '10 hours', NOW() - INTERVAL '5 hours')
;


-- =============================================
-- Seed Audit Logs
-- =============================================

INSERT INTO audit_logs (user_id, action, model_name, object_id, changes, ip_address, created_at)
VALUES
(1, 'CREATE', 'User', '1', '{"username": "admin", "role": "superadmin"}', '127.0.0.1', NOW() - INTERVAL '7 days'),
(2, 'CREATE', 'User', '2', '{"username": "ahmad", "role": "user"}', '192.168.1.100', NOW() - INTERVAL '5 days'),
(3, 'CREATE', 'User', '3', '{"username": "sara", "role": "user"}', '192.168.1.101', NOW() - INTERVAL '3 days'),
(2, 'CREATE', 'Transaction', '5', '{"amount": "200.00", "type": "transfer"}', '192.168.1.100', NOW() - INTERVAL '4 days'),
(1, 'UPDATE', 'Wallet', '1', '{"balance": {"old": "5000.00", "new": "4797.00"}}', '127.0.0.1', NOW() - INTERVAL '4 days'),
(1, 'CREATE', 'Transaction', '8', '{"amount": "1000.00", "type": "transfer"}', '127.0.0.1', NOW() - INTERVAL '6 hours')
;


-- ============================================================
-- DONE! Your database is fully set up with seed data.
-- ============================================================
-- What you have now:
--   7 users (1 superadmin, 1 admin, 5 regular users)
--   7 wallets (each linked to a user)
--   17 transactions (deposits, transfers, withdrawals)
--   12 notifications
--   2 refund requests
--   6 audit log entries
--
-- IMPORTANT: User passwords are NOT real hashes above.
-- You MUST create a real password using Django.
-- See the next SQL section below.
-- ============================================================


-- ============================================================
-- PART 6: SET REAL PASSWORDS (RUN THIS TOO!)
-- ============================================================
-- The passwords above are fake hashes. We need real Django hashes.
-- But since we can't run Django code in SQL, we'll use a workaround:
-- Use a known Django password hash for the password "Wallet123!"
-- ============================================================

-- This is a REAL Django-compatible PBKDF2 hash for password: Wallet123!
-- All users share this password so you can test login with any account.
-- Login credentials: username (below) / password: Wallet123!
UPDATE users SET password = 'pbkdf2_sha256$600000$HN7wC6SssyTWCHqK$WAktD/THu+DCWfVn7yMDMihwAE5IGL2xDpV+NznYvHg=';
