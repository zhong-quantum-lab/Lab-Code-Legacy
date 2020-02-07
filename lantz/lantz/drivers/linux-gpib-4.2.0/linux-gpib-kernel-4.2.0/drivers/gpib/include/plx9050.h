/***************************************************************************
                          plx9050.h  -  description
                             -------------------
  Header for plx9050 pci chip

    copyright            : (C) 2002 by Frank Mori Hess
    email                : fmhess@users.sourceforge.net
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

#ifndef _PLX9050_GPIB_H
#define _PLX9050_GPIB_H

// plx pci chip registers and bits
enum
{
	PLX9050_INTCSR_REG = 0x4c,
	PLX9050_CNTRL_REG = 0x50
};

enum plx9050_intcsr_bits
{
	PLX9050_LINTR1_EN_BIT = 0x1,
	PLX9050_LINTR1_POLARITY_BIT = 0x2,
	PLX9050_LINTR1_STATUS_BIT = 0x4,
	PLX9050_LINTR2_EN_BIT = 0x8,
	PLX9050_LINTR2_POLARITY_BIT = 0x10,
	PLX9050_LINTR2_STATUS_BIT = 0x20,
	PLX9050_PCI_INTR_EN_BIT = 0x40,
	PLX9050_SOFT_INTR_BIT = 0x80,
	PLX9050_LINTR1_SELECT_ENABLE_BIT = 0x100,	//9052 extension
	PLX9050_LINTR2_SELECT_ENABLE_BIT = 0x200,	//9052 extension
	PLX9050_LINTR1_EDGE_CLEAR_BIT = 0x400,	//9052 extension
	PLX9050_LINTR2_EDGE_CLEAR_BIT = 0x800,	//9052 extension
};

enum plx9050_cntrl_bits
{
	PLX9050_WAITO_NOT_USER0_SELECT_BIT = 0x1,
	PLX9050_USER0_OUTPUT_BIT = 0x2,
	PLX9050_USER0_DATA_BIT = 0x4,
	PLX9050_LLOCK_NOT_USER1_SELECT_BIT = 0x8,
	PLX9050_USER1_OUTPUT_BIT = 0x10,
	PLX9050_USER1_DATA_BIT = 0x20,
	PLX9050_CS2_NOT_USER2_SELECT_BIT = 0x40,
	PLX9050_USER2_OUTPUT_BIT = 0x80,
	PLX9050_USER2_DATA_BIT = 0x100,
	PLX9050_CS3_NOT_USER3_SELECT_BIT = 0x200,
	PLX9050_USER3_OUTPUT_BIT = 0x400,
	PLX9050_USER3_DATA_BIT = 0x800,
	PLX9050_PCIBAR_ENABLE_MASK = 0x3000,
	PLX9050_PCIBAR_MEMORY_AND_IO_ENABLE_BITS = 0x0,
	PLX9050_PCIBAR_MEMORY_NO_IO_ENABLE_BITS = 0x1000,
	PLX9050_PCIBAR_IO_NO_MEMORY_ENABLE_BITS = 0x2000,
	PLX9050_PCIBAR_MEMORY_AND_IO_TOO_ENABLE_BITS = 0x3000,
	PLX9050_PCI_READ_MODE_BIT = 0x4000,
	PLX9050_PCI_READ_WITH_WRITE_FLUSH_MODE_BIT = 0x8000,
	PLX9050_PCI_READ_NO_FLUSH_MODE_BIT = 0x10000,
	PLX9050_PCI_READ_NO_WRITE_MODE_BIT = 0x20000,
	PLX9050_PCI_WRITE_MODE_BIT = 0x40000,
	PLX9050_PCI_RETRY_DELAY_MASK = 0x780000,
	PLX9050_DIRECT_SLAVE_LOCK_ENABLE_BIT = 0x800000,
	PLX9050_EEPROM_CLOCK_BIT = 0x1000000,
	PLX9050_EEPROM_CHIP_SELECT_BIT = 0x2000000,
	PLX9050_WRITE_TO_EEPROM_BIT = 0x4000000,
	PLX9050_READ_EEPROM_DATA_BIT = 0x8000000,
	PLX9050_EEPROM_VALID_BIT = 0x10000000,
	PLX9050_RELOAD_CONFIG_REGISTERS_BIT = 0x20000000,
	PLX9050_PCI_SOFTWARE_RESET_BIT = 0x40000000,
	PLX9050_MASK_REVISION_BIT = 0x80000000
};
static inline unsigned PLX9050_PCI_RETRY_DELAY_BITS(unsigned clocks)
{
	return ((clocks / 8) << 19) & PLX9050_PCI_RETRY_DELAY_MASK;
}

#endif	// _PLX9050_GPIB_H
