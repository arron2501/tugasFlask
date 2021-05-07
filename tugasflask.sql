-- phpMyAdmin SQL Dump
-- version 5.0.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 07 Bulan Mei 2021 pada 18.45
-- Versi server: 10.4.17-MariaDB
-- Versi PHP: 8.0.1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `tugasflask`
--

-- --------------------------------------------------------

--
-- Struktur dari tabel `banners`
--

CREATE TABLE `banners` (
  `id` int(10) NOT NULL,
  `banner` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data untuk tabel `banners`
--

INSERT INTO `banners` (`id`, `banner`, `created_at`, `updated_at`) VALUES
(10, 'uploads/banners/5.jpg', '2021-03-07 16:30:17', '2021-03-07 16:30:17'),
(11, 'uploads/banners/7.jpg', '2021-03-07 16:30:49', '2021-03-07 19:54:01'),
(14, 'uploads/banners/8.png', '2021-03-07 19:53:48', '2021-03-07 19:53:48'),
(15, 'uploads/banners/Mockup_IG_NARUTO-13.jpg', '2021-03-08 11:28:03', '2021-03-08 11:28:03'),
(16, 'uploads/banners/Mockup_IG_NARUTO-8.jpg', '2021-03-08 11:29:00', '2021-03-08 11:29:00');

-- --------------------------------------------------------

--
-- Struktur dari tabel `devices`
--

CREATE TABLE `devices` (
  `id` int(10) UNSIGNED NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data untuk tabel `devices`
--

INSERT INTO `devices` (`id`, `name`, `created_at`, `updated_at`) VALUES
(9, 'iPhone 11', '2021-03-07 16:33:08', '2021-03-07 16:33:08'),
(10, 'iPhone 11 Pro', '2021-03-07 16:33:26', '2021-03-07 16:33:26'),
(11, 'iPhone 11 Pro Max', '2021-03-07 16:33:32', '2021-03-07 16:33:32'),
(12, 'iPhone 12', '2021-03-07 16:33:38', '2021-03-07 16:33:38'),
(14, 'iPhone 12 Pro', '2021-03-07 16:33:52', '2021-03-07 19:53:21'),
(16, 'iPhone 12 Pro Max', '2021-03-07 19:53:07', '2021-03-07 19:53:07');

-- --------------------------------------------------------

--
-- Struktur dari tabel `products`
--

CREATE TABLE `products` (
  `id` int(10) UNSIGNED NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `price` int(11) DEFAULT NULL,
  `mockup` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data untuk tabel `products`
--

INSERT INTO `products` (`id`, `title`, `description`, `price`, `mockup`, `created_at`, `updated_at`) VALUES
(22, 'Astronaut Case 002', 'Cool case!!', 109000, 'uploads/mockups/Mockup_IG_ASTRO-8.jpg', '2021-03-07 16:25:07', '2021-03-07 19:52:26'),
(25, 'testwkwkte', 'test', 23, 'uploads/mockups/Mockup_IG_ASTRO-9.jpg', '2021-03-08 11:12:40', '2021-03-08 11:12:40'),
(26, 's', 'd', 3, 'uploads/mockups/Mockup_IG_ASTRO-8.jpg', '2021-03-08 11:17:47', '2021-03-08 11:17:47'),
(27, 'bb', 'bb', 555, 'uploads/mockups/Mockup_IG_ASTRO-7.jpg', '2021-03-08 11:22:09', '2021-03-08 11:22:09'),
(28, 'ah', 'ah', 12, 'uploads/mockups/Mockup_IG_ASTRO-3.jpg', '2021-03-08 11:22:39', '2021-03-08 11:22:39');

-- --------------------------------------------------------

--
-- Struktur dari tabel `users`
--

CREATE TABLE `users` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `role_id` bigint(20) UNSIGNED DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data untuk tabel `users`
--

INSERT INTO `users` (`id`, `role_id`, `name`, `email`, `password`, `created_at`, `updated_at`) VALUES
(97, 1, 'Rivaltino Arron', 'arron2501@gmail.com', '202cb962ac59075b964b07152d234b70', '2021-05-07 16:44:12', '2021-05-07 16:44:12');

--
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `banners`
--
ALTER TABLE `banners`
  ADD PRIMARY KEY (`id`);

--
-- Indeks untuk tabel `devices`
--
ALTER TABLE `devices`
  ADD PRIMARY KEY (`id`);

--
-- Indeks untuk tabel `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`id`);

--
-- Indeks untuk tabel `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT untuk tabel yang dibuang
--

--
-- AUTO_INCREMENT untuk tabel `banners`
--
ALTER TABLE `banners`
  MODIFY `id` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT untuk tabel `devices`
--
ALTER TABLE `devices`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT untuk tabel `products`
--
ALTER TABLE `products`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=30;

--
-- AUTO_INCREMENT untuk tabel `users`
--
ALTER TABLE `users`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=98;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
