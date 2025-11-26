# Cluster Part Numbers & Variants

## Part Number Format

Porsche part numbers follow the pattern: `996.641.xxx.xx`

Example: `996.641.507.01`

## Known Cluster Variants

### 986 Boxster Clusters

| Part Number | Year | Market | Features |
|-------------|------|--------|----------|
| 996.641.503.xx | 1997-1999 | US | Basic, no OBC |
| 996.641.507.xx | 1997-1999 | EU | Basic, no OBC |
| 996.641.603.xx | 2000-2002 | US | Updated style |
| 996.641.607.xx | 2000-2002 | EU | Updated style |
| 996.641.703.xx | 2003-2004 | US | Final revision |
| 996.641.707.xx | 2003-2004 | EU | Final revision |

### 996 Carrera Clusters

| Part Number | Year | Market | Features |
|-------------|------|--------|----------|
| 996.641.505.xx | 1998-2001 | US | May have OBC |
| 996.641.509.xx | 1998-2001 | EU | May have OBC |
| 996.641.605.xx | 2002-2004 | US | Updated |
| 996.641.609.xx | 2002-2004 | EU | Updated |

### Special Variants

| Part Number | Model | Notes |
|-------------|-------|-------|
| 996.641.xxx.xx | GT3 | Different redline, 89L tank |
| 996.641.xxx.xx | Turbo | Different boost gauge area |

**Note:** Part numbers vary by exact features (OBC, oil pressure, etc.)

## EEPROM Variants

| Cluster Type | EEPROM | Size |
|--------------|--------|------|
| 1997-2001 (early) | 93C56B | 256 bytes |
| 2001-2004 (late) | 93C86 | 2048 bytes |

## Compatibility Matrix

### 986 ↔ 996 Swap

| Feature | Compatible? | Notes |
|---------|-------------|-------|
| Physical fit | Yes | Same mounting |
| Connector | Yes | Same pinout |
| Speedometer | Yes | |
| Tachometer | Yes | Same redline |
| Fuel gauge | Mostly | May need EEPROM adjustment |
| OBC | Yes | May need enabling |

### Year-to-Year Compatibility

| From | To | Compatible? | Notes |
|------|----|-------------|-------|
| 1997-1999 | 1997-1999 | Yes | Direct swap |
| 2000-2004 | 2000-2004 | Yes | Direct swap |
| 1997-1999 | 2000-2004 | Partial | Different styling, EEPROM |
| 2000-2004 | 1997-1999 | Partial | Different styling, EEPROM |

## Identifying Your Cluster

### Label Location

Part number is printed on:
- Label on back of cluster
- Sticker inside housing
- EEPROM data (can be read)

### Visual Identification

**Early (1997-1999):**
- White text on black gauges
- Simpler LCD
- 93C56B EEPROM

**Later (2000-2004):**
- Updated font/styling
- More LCD features
- 93C86 EEPROM (most)

## Sourcing Used Clusters

### Good Sources

- eBay (verify part number)
- Porsche forums classifieds
- 986/996 breakers/dismantlers

### What to Check

1. Matching part number suffix for your market (US/EU)
2. Mileage displayed (will need adjustment)
3. LCD condition (pixels)
4. Physical damage
5. EEPROM type if known

### Pricing Guide (Used)

| Condition | Price Range |
|-----------|-------------|
| Working, high miles | $100-200 |
| Working, good LCD | $200-350 |
| Low miles, mint | $350-500+ |
| For parts only | $50-100 |

## OEM vs Aftermarket

### OEM Porsche

- Best compatibility
- Expensive ($1000+)
- Getting rare for early models

### Used OEM

- Recommended option
- May need EEPROM work
- Verify condition

### Aftermarket/Rebuilt

- Some companies rebuild clusters
- Quality varies
- Warranty important
