-- ============================================================================
-- VP INFO SOLUTIONS PVT LTD - TALLY CERTIFIED PARTNER
-- Application: "Antigravity" Lead Generation & Tracking System
-- Target RDBMS: MySQL 8.0+
-- Database Schema, Foreign Key Constraints, Seed Data & Power BI Views
-- ============================================================================

CREATE DATABASE IF NOT EXISTS `vp_antigravity_db`
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `vp_antigravity_db`;

-- Drop existing tables if needed (in reverse dependency order)
DROP VIEW IF EXISTS `vw_powerbi_monthly_trends`;
DROP VIEW IF EXISTS `vw_powerbi_rm_team_summary`;
DROP VIEW IF EXISTS `vw_powerbi_sales_rep_summary`;
DROP VIEW IF EXISTS `vw_powerbi_leads_master`;
DROP TABLE IF EXISTS `lead_activity_logs`;
DROP TABLE IF EXISTS `leads`;
DROP TABLE IF EXISTS `users`;

-- ----------------------------------------------------------------------------
-- 1. USERS TABLE
-- Supports Role-Based Access Control (Admin, RM, Sales Person)
-- Self-referential foreign key (rm_id) maps Sales Persons to their Relationship Manager
-- ----------------------------------------------------------------------------
CREATE TABLE `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `full_name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(100) NOT NULL UNIQUE,
    `phone` VARCHAR(20) DEFAULT NULL,
    `role` ENUM('Admin', 'RM', 'Sales Person') NOT NULL,
    `rm_id` INT DEFAULT NULL,
    `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_users_rm`
        FOREIGN KEY (`rm_id`) REFERENCES `users` (`id`)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    INDEX `idx_users_role` (`role`),
    INDEX `idx_users_rm` (`rm_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 2. LEADS TABLE
-- Tracks prospective clients, Tally products of interest, and stages
-- ----------------------------------------------------------------------------
CREATE TABLE `leads` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `lead_name` VARCHAR(100) NOT NULL,
    `business_name` VARCHAR(150) NOT NULL,
    `phone` VARCHAR(20) NOT NULL,
    `email` VARCHAR(100) DEFAULT NULL,
    `industry` VARCHAR(80) NOT NULL,
    `interested_product` VARCHAR(100) NOT NULL,
    `status` ENUM('New', 'Contacted', 'Demo Scheduled', 'Negotiation', 'Won', 'Lost') NOT NULL DEFAULT 'New',
    `estimated_value` DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    `notes` TEXT DEFAULT NULL,
    `sales_person_id` INT NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_leads_sales_person`
        FOREIGN KEY (`sales_person_id`) REFERENCES `users` (`id`)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    INDEX `idx_leads_status` (`status`),
    INDEX `idx_leads_sales_person` (`sales_person_id`),
    INDEX `idx_leads_product` (`interested_product`),
    INDEX `idx_leads_industry` (`industry`),
    INDEX `idx_leads_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 3. LEAD ACTIVITY LOGS
-- Complete audit trail for lead stage transitions, notes, and reassignments
-- ----------------------------------------------------------------------------
CREATE TABLE `lead_activity_logs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `lead_id` INT NOT NULL,
    `action` VARCHAR(50) NOT NULL,
    `details` TEXT DEFAULT NULL,
    `performed_by_id` INT DEFAULT NULL,
    `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_log_lead`
        FOREIGN KEY (`lead_id`) REFERENCES `leads` (`id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT `fk_log_user`
        FOREIGN KEY (`performed_by_id`) REFERENCES `users` (`id`)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    INDEX `idx_log_lead` (`lead_id`),
    INDEX `idx_log_timestamp` (`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 4. POWER BI READY VIEWS
-- Optimized for direct import or direct query in Microsoft Power BI Desktop
-- ============================================================================

-- A. Master Leads Denormalized View (Star-Schema fact table format)
CREATE OR REPLACE VIEW `vw_powerbi_leads_master` AS
SELECT 
    l.id AS `LeadID`,
    l.lead_name AS `ContactPerson`,
    l.business_name AS `Company`,
    l.phone AS `Phone`,
    COALESCE(l.email, '') AS `Email`,
    l.industry AS `Industry`,
    l.interested_product AS `TallyProduct`,
    l.status AS `Stage`,
    l.estimated_value AS `DealValueINR`,
    CASE WHEN l.status = 'Won' THEN 1 ELSE 0 END AS `IsClosedWon`,
    CASE WHEN l.status = 'Lost' THEN 1 ELSE 0 END AS `IsClosedLost`,
    CASE WHEN l.status NOT IN ('Won', 'Lost') THEN 1 ELSE 0 END AS `IsOpenPipeline`,
    sp.id AS `SalesRepID`,
    sp.full_name AS `SalesRepName`,
    sp.email AS `SalesRepEmail`,
    rm.id AS `RMID`,
    COALESCE(rm.full_name, 'Direct / None') AS `RelationshipManagerName`,
    l.created_at AS `LeadCreatedTimestamp`,
    DATE(l.created_at) AS `LeadCreatedDate`,
    l.updated_at AS `LeadUpdatedTimestamp`,
    DATEDIFF(l.updated_at, l.created_at) AS `CycleDays`,
    l.notes AS `LatestNotes`
FROM `leads` l
INNER JOIN `users` sp ON l.sales_person_id = sp.id
LEFT JOIN `users` rm ON sp.rm_id = rm.id;

-- B. Sales Representative Performance Aggregation View
CREATE OR REPLACE VIEW `vw_powerbi_sales_rep_summary` AS
SELECT 
    sp.id AS `SalesRepID`,
    sp.full_name AS `SalesRepName`,
    COALESCE(rm.full_name, 'No RM Assigned') AS `ReportingManager`,
    COUNT(l.id) AS `TotalLeadsAssigned`,
    SUM(CASE WHEN l.status = 'Won' THEN 1 ELSE 0 END) AS `WonDeals`,
    SUM(CASE WHEN l.status = 'Lost' THEN 1 ELSE 0 END) AS `LostDeals`,
    SUM(CASE WHEN l.status NOT IN ('Won', 'Lost') THEN 1 ELSE 0 END) AS `ActiveDeals`,
    SUM(l.estimated_value) AS `TotalPipelineValueINR`,
    SUM(CASE WHEN l.status = 'Won' THEN l.estimated_value ELSE 0 END) AS `WonRevenueINR`,
    ROUND((SUM(CASE WHEN l.status = 'Won' THEN 1.0 ELSE 0.0 END) / NULLIF(COUNT(l.id), 0)) * 100, 2) AS `ConversionRatePct`
FROM `users` sp
LEFT JOIN `users` rm ON sp.rm_id = rm.id
LEFT JOIN `leads` l ON l.sales_person_id = sp.id
WHERE sp.role = 'Sales Person' AND sp.is_active = TRUE
GROUP BY sp.id, sp.full_name, rm.full_name;

-- C. Relationship Manager Team Performance Aggregation View
CREATE OR REPLACE VIEW `vw_powerbi_rm_team_summary` AS
SELECT 
    rm.id AS `RMID`,
    rm.full_name AS `RelationshipManagerName`,
    COUNT(DISTINCT sp.id) AS `TeamHeadcount`,
    COUNT(l.id) AS `TeamTotalLeads`,
    SUM(CASE WHEN l.status = 'Won' THEN 1 ELSE 0 END) AS `TeamWonDeals`,
    SUM(CASE WHEN l.status = 'Lost' THEN 1 ELSE 0 END) AS `TeamLostDeals`,
    SUM(CASE WHEN l.status NOT IN ('Won', 'Lost') THEN 1 ELSE 0 END) AS `TeamActiveDeals`,
    SUM(l.estimated_value) AS `TeamTotalPipelineINR`,
    SUM(CASE WHEN l.status = 'Won' THEN l.estimated_value ELSE 0 END) AS `TeamWonRevenueINR`,
    ROUND((SUM(CASE WHEN l.status = 'Won' THEN 1.0 ELSE 0.0 END) / NULLIF(COUNT(l.id), 0)) * 100, 2) AS `TeamConversionRatePct`
FROM `users` rm
INNER JOIN `users` sp ON sp.rm_id = rm.id
LEFT JOIN `leads` l ON l.sales_person_id = sp.id
WHERE rm.role = 'RM' AND rm.is_active = TRUE
GROUP BY rm.id, rm.full_name;

-- D. Monthly Sales Trend View for Forecasting
CREATE OR REPLACE VIEW `vw_powerbi_monthly_trends` AS
SELECT 
    DATE_FORMAT(l.created_at, '%Y-%m') AS `YearMonth`,
    l.interested_product AS `Product`,
    COUNT(l.id) AS `MonthlyLeads`,
    SUM(CASE WHEN l.status = 'Won' THEN 1 ELSE 0 END) AS `WonDeals`,
    SUM(l.estimated_value) AS `PipelineValueINR`,
    SUM(CASE WHEN l.status = 'Won' THEN l.estimated_value ELSE 0 END) AS `ClosedWonRevenueINR`
FROM `leads` l
GROUP BY DATE_FORMAT(l.created_at, '%Y-%m'), l.interested_product
ORDER BY `YearMonth` DESC;

-- ============================================================================
-- 5. INITIAL SAMPLE SEED DATA
-- Default Passwords (pre-hashed with SHA256 salt 'vp_info_tally_2026'):
-- Admin: admin / admin123
-- RMs: rm_vikram, rm_ananya / rm123
-- Sales Persons: sales_amit, sales_priya, sales_rohit, sales_sneha / sales123
-- ============================================================================

INSERT INTO `users` (`id`, `username`, `password_hash`, `full_name`, `email`, `phone`, `role`, `rm_id`, `is_active`) VALUES
(1, 'admin', '84beea3714b3d3ae07bb6a2080344b1c2018ea1b021d7b32252c1e7372d80cbe', 'Rajesh Sharma', 'rajesh.sharma@vpinfosolutions.com', '+91 98201 11222', 'Admin', NULL, TRUE),
(2, 'rm_vikram', '39cf629e4bf67e34f6bbd688cf6ea37482590216b471677c7ec21868352528db', 'Vikram Malhotra', 'vikram.m@vpinfosolutions.com', '+91 98111 22334', 'RM', NULL, TRUE),
(3, 'rm_ananya', '39cf629e4bf67e34f6bbd688cf6ea37482590216b471677c7ec21868352528db', 'Ananya Deshmukh', 'ananya.d@vpinfosolutions.com', '+91 98222 33445', 'RM', NULL, TRUE),
(4, 'sales_amit', 'a8600d33e9d8e705cb5cb5f29d91f4ae8b7cbf319a3b684cb4427494f6c4ff54', 'Amit Verma', 'amit.v@vpinfosolutions.com', '+91 98765 43210', 'Sales Person', 2, TRUE),
(5, 'sales_priya', 'a8600d33e9d8e705cb5cb5f29d91f4ae8b7cbf319a3b684cb4427494f6c4ff54', 'Priya Nair', 'priya.n@vpinfosolutions.com', '+91 98765 43211', 'Sales Person', 2, TRUE),
(6, 'sales_rohit', 'a8600d33e9d8e705cb5cb5f29d91f4ae8b7cbf319a3b684cb4427494f6c4ff54', 'Rohit Mehta', 'rohit.m@vpinfosolutions.com', '+91 98765 43212', 'Sales Person', 3, TRUE),
(7, 'sales_sneha', 'a8600d33e9d8e705cb5cb5f29d91f4ae8b7cbf319a3b684cb4427494f6c4ff54', 'Sneha Kulkarni', 'sneha.k@vpinfosolutions.com', '+91 98765 43213', 'Sales Person', 3, TRUE);

INSERT INTO `leads` (`id`, `lead_name`, `business_name`, `phone`, `email`, `industry`, `interested_product`, `status`, `estimated_value`, `notes`, `sales_person_id`, `created_at`) VALUES
(1, 'Suresh Patel', 'Apex Engineering & Auto Components', '+91 98230 45678', 'spatel@apexengg.co.in', 'Manufacturing', 'TallyPrime Silver/Gold', 'Won', 54000.00, 'Closed 3 Multi-User TallyPrime Gold licenses with GST integration.', 4, '2026-10-15 10:30:00'),
(2, 'Manish Gupta', 'Radhika Sarees & Textiles', '+91 98901 23456', 'manish@radhikatex.com', 'Textiles & Retail', 'Tally.ERP 9 Upgrade to Prime', 'Demo Scheduled', 22500.00, 'Running old Tally ERP 9 Release 5.4. Wants demo on e-Invoicing in Prime 4.1.', 4, '2026-10-18 14:15:00'),
(3, 'Col. K.S. Rathore', 'BlueStar Cold Chain & Logistics', '+91 97112 34567', 'ks.rathore@bluestarcold.com', 'Logistics & Warehousing', 'Tally on Cloud', 'Negotiation', 78000.00, '12 branch locations need concurrent access via secured cloud instance.', 4, '2026-10-22 16:45:00'),
(4, 'Sunil Bansal', 'Bansal Agro Chem Traders', '+91 98450 12987', 'sunil@bansalagro.in', 'FMCG / Agro', 'Annual Maintenance Contract (AMC)', 'New', 15000.00, 'Inquiry received from website for Comprehensive Annual Maintenance Contract.', 4, '2026-10-28 11:00:00'),
(5, 'Dr. Arvind Chordia', 'Lifeline Multi-Speciality Clinic', '+91 99221 87654', 'finance@lifelinehosp.org', 'Healthcare & Pharma', 'Tally Customization (TDL)', 'Won', 95000.00, 'Customized Doctor payout modules and pharmacy inventory batch sync TDL developed.', 5, '2026-10-16 12:20:00'),
(6, 'Harish Shah', 'Shah Diamond Tools Pvt Ltd', '+91 98210 65432', 'hshah@shahdiamond.com', 'Industrial Hardware', 'Tally Server 9', 'Negotiation', 135000.00, 'High concurrency bottleneck on LAN; moving to dedicated Tally Server 9.', 5, '2026-10-20 15:10:00'),
(7, 'Kavita Rao', 'Zest Lifestyle Fashion', '+91 98401 54321', 'kavita.rao@zestretail.in', 'Retail & Apparel', 'TallyPrime Silver/Gold', 'Contacted', 36000.00, 'Opening 2 new stores in Bangalore. Needs barcode billing setup.', 5, '2026-10-26 09:40:00'),
(8, 'Nitin Gadgil', 'Western Horizon Infra & Builders', '+91 98200 98765', 'accounts@westernhorizon.co.in', 'Construction & Real Estate', 'Tally Customization (TDL)', 'Won', 120000.00, 'Site-wise job costing, RERA compliance reports customized and deployed.', 6, '2026-10-12 11:30:00'),
(9, 'Pooja Hegde', 'Spices of India Exporters', '+91 97400 87654', 'pooja@spicesofindia.biz', 'Import & Export', 'Tally API & ERP Integration', 'Demo Scheduled', 85000.00, 'Wants custom API bridge between Shopify web orders and Tally Sales Vouchers.', 6, '2026-10-24 14:00:00'),
(10, 'Ramesh Somani', 'Somani Paper Mills Ltd', '+91 98251 23411', 'somani.r@somanipaper.com', 'Paper & Packaging', 'Tally.ERP 9 Upgrade to Prime', 'Lost', 30000.00, 'Postponed IT upgrade decision to next fiscal quarter due to plant relocation.', 6, '2026-10-19 17:15:00'),
(11, 'Deepak Joshi', 'Zenith Cloud IT Services', '+91 98801 34567', 'djoshi@zenithcloudit.com', 'IT & Software Services', 'Annual Maintenance Contract (AMC)', 'Won', 28000.00, 'Signed 2-year AMC package with dedicated priority remote support.', 7, '2026-10-14 13:45:00'),
(12, 'Vikram Singh', 'Royal Heritage Hotels & Resorts', '+91 98290 11223', 'gm.finance@royalheritage.in', 'Hospitality', 'Tally on Cloud', 'Contacted', 62000.00, '3 properties need central accounting access with role-based vouchers.', 7, '2026-10-23 10:20:00'),
(13, 'Farhan Qureshi', 'Precision Die Castings', '+91 98212 99887', 'farhan@precisiondie.com', 'Manufacturing', 'TallyPrime Silver/Gold', 'New', 45000.00, 'Inbound referral from existing customer Apex Engineering.', 7, '2026-10-29 16:30:00');
