CREATE TABLE `todos` (
  `id` int(11) NOT NULL,
  `task` varchar(45) NOT NULL,
  `dueby` date NOT NULL,
  `status` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1