-- Schema para el sistema de tickets (GLPI) del Ayuntamiento de Aranjuez
-- Creado para ser ejecutado en MySQL / MariaDB (phpMyAdmin)

-- =========================================================
-- 1. CREACIÓN DE TABLAS
-- =========================================================

CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT
);

CREATE TABLE departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE,
    first_name VARCHAR(50),
    last_name VARCHAR(100),
    role_id INT NOT NULL,
    department_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id),
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL
);

CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    parent_id INT DEFAULT NULL,
    is_visible_to_users BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE CASCADE
);

CREATE TABLE tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status ENUM('Nuevo', 'Asignado', 'En curso', 'Pendiente', 'Resuelto', 'Cerrado') DEFAULT 'Nuevo',
    priority ENUM('Baja', 'Media', 'Alta', 'Urgente') DEFAULT 'Media',
    category_id INT,
    requester_id INT NOT NULL,
    assignee_id INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    FOREIGN KEY (requester_id) REFERENCES users(id),
    FOREIGN KEY (assignee_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE ticket_comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT NOT NULL,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- =========================================================
-- 2. DATOS INICIALES (INSERTS)
-- =========================================================

-- ROLES
INSERT INTO roles (name, description) VALUES
('Admin', 'Administrador del sistema con acceso total'),
('Tecnico', 'Técnico de soporte (Sistemas), puede ver tickets y áreas de sistemas'),
('Usuario', 'Usuario estándar del Ayuntamiento');

-- DEPARTAMENTOS BASICOS (Ejemplos iniciales)
INSERT INTO departments (name) VALUES
('Alcaldía'),
('Recursos Humanos'),
('Intervención'),
('Urbanismo'),
('Sistemas y Nuevas Tecnologías');

-- CATEGORÍAS
-- Variables para guardar los IDs padres al insertar

-- 1. Puesto de trabajo
INSERT INTO categories (name, parent_id, is_visible_to_users) VALUES ('Puesto de trabajo', NULL, TRUE);
SET @cat_puesto := LAST_INSERT_ID();
INSERT INTO categories (name, parent_id, is_visible_to_users) VALUES 
('PC / Portátil / Móvil', @cat_puesto, TRUE),
('Impresora / Escaner', @cat_puesto, TRUE),
('Periféricos (ratón, teclado, monitor)', @cat_puesto, TRUE),
('Tótems', @cat_puesto, TRUE);

-- 2. Software y aplicaciones
INSERT INTO categories (name, parent_id, is_visible_to_users) VALUES ('Software y aplicaciones', NULL, TRUE);
SET @cat_software := LAST_INSERT_ID();

INSERT INTO categories (name, parent_id, is_visible_to_users) VALUES ('Administración Electrónica', @cat_software, TRUE);
SET @cat_admon_elec := LAST_INSERT_ID();
INSERT INTO categories (name, parent_id, is_visible_to_users) VALUES 
('SicalWin', @cat_admon_elec, TRUE),
('Firmadoc', @cat_admon_elec, TRUE),
('AytosCES', @cat_admon_elec, TRUE),
('Accede', @cat_admon_elec, TRUE),
('WinGT', @cat_admon_elec, TRUE),
('Sede Electrónica', @cat_admon_elec, TRUE),
('Sigep', @cat_admon_elec, TRUE),
('WCronos (fichajes y permisos)', @cat_admon_elec, TRUE),
('Chronos (Olivas)', @cat_admon_elec, TRUE),
('Eurocop', @cat_admon_elec, TRUE),
('Medtra', @cat_admon_elec, TRUE),
('Remuda', @cat_admon_elec, TRUE),
('S Tec está preparando de nuevo un GIS', @cat_admon_elec, TRUE); -- Ojo al nombre, lo mantengo literal

INSERT INTO categories (name, parent_id, is_visible_to_users) VALUES 
('Correo electrónico', @cat_software, TRUE),
('Ofimática (LibreOffice / Office)', @cat_software, TRUE),
('Certificado Digital', @cat_software, TRUE),
('Firma electrónica', @cat_software, TRUE),
('Comunicación con otros organismos (INE, hacienda, tesorería SS...)', @cat_software, TRUE),
('Teams, zooms, meets...', @cat_software, TRUE);

INSERT INTO categories (name, parent_id, is_visible_to_users) VALUES ('Aplicaciones propias (de Fernando)', @cat_software, TRUE);
SET @cat_propias := LAST_INSERT_ID();
INSERT INTO categories (name, parent_id, is_visible_to_users) VALUES 
('Mantenimiento de las actuales.', @cat_propias, TRUE),
('Desarrollo de nuevas herramientas.', @cat_propias, TRUE);

-- 3. Redes y Conectividad
INSERT INTO categories (name, parent_id, is_visible_to_users) VALUES ('Redes y Conectividad', NULL, TRUE);
SET @cat_redes := LAST_INSERT_ID();
INSERT INTO categories (name, parent_id, is_visible_to_users) VALUES 
('Wi-Fi', @cat_redes, TRUE),
('Internet', @cat_redes, TRUE),
('Carpeta de red', @cat_redes, TRUE),
('Telefonía', @cat_redes, TRUE),
('Acceso remoto', @cat_redes, TRUE);

-- 4. Acceso y Seguridad
INSERT INTO categories (name, parent_id, is_visible_to_users) VALUES ('Acceso y Seguridad', NULL, TRUE);
SET @cat_acceso := LAST_INSERT_ID();
INSERT INTO categories (name, parent_id, is_visible_to_users) VALUES 
('Cambio de contraseña', @cat_acceso, TRUE),
('Alta / Baja de usuario', @cat_acceso, TRUE),
('Solicitud permisos', @cat_acceso, TRUE);

-- 5. Sistemas (esto no se mostraría a los usuarios, sólo para nosotros)
-- PONEMOS is_visible_to_users = FALSE
INSERT INTO categories (name, parent_id, is_visible_to_users) VALUES ('Sistemas', NULL, FALSE);
SET @cat_sistemas := LAST_INSERT_ID();
INSERT INTO categories (name, parent_id, is_visible_to_users) VALUES 
('Servidores', @cat_sistemas, FALSE),
('Almacenamiento', @cat_sistemas, FALSE),
('Bases de datos', @cat_sistemas, FALSE),
('Desarrollos (como el script de padrón ¿?)', @cat_sistemas, FALSE),
('Copias de seguridad', @cat_sistemas, FALSE),
('Firewall', @cat_sistemas, FALSE),
('Switches', @cat_sistemas, FALSE),
('Puntos de Acceso', @cat_sistemas, FALSE),
('Centralita', @cat_sistemas, FALSE),
('Licenciamiento', @cat_sistemas, FALSE);

-- 6. Sala de capacitación digital
INSERT INTO categories (name, parent_id, is_visible_to_users) VALUES ('Sala de capacitación digital', NULL, TRUE);

-- 7. Otros
INSERT INTO categories (name, parent_id, is_visible_to_users) VALUES ('Otros', NULL, TRUE);
SET @cat_otros := LAST_INSERT_ID();
INSERT INTO categories (name, parent_id, is_visible_to_users) VALUES 
('Pendiente clasificar', @cat_otros, TRUE);
