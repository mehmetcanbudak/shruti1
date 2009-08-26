// Copyright 2009 Olivier Gillet. All rights reserved
//
// Author: Olivier Gillet (ol.gillet@gmail.com)
//
// Parameter editor.

#ifndef HARDWARE_SHRUTI_SHRUTI_H_
#define HARDWARE_SHRUTI_SHRUTI_H_

#include "hardware/base/base.h"

#ifndef __TEST__
#define FAST_SIGNAL_PROCESSING
#endif  // !__TEST__

// #define SOFTWARE_VCA

namespace hardware_shruti {

// Rate of the main timer. For now, 1 sample is generated per tick, but we might
// want to do something different to achieve other sample rates
// (20kHz or 16kHz).
static const uint16_t kMainTimerRate = 31250;
static const uint16_t kSampleRate = 31250;

static const uint16_t kDisplayBaudRate = 2400;

static const uint8_t kControlRate = 32;
static const uint8_t kAudioBlockSize = kControlRate;
static const uint8_t kAudioBufferSize = kAudioBlockSize * 4;

// ---- Wirings ----------------------------------------------------------------

// Serial/UART output.
static const uint8_t kPinMidiInRx = 0;
static const uint8_t kPinMidiThruTx = 1;
static const uint8_t kPinLcdTx = 2;

// Shift register / muxes.
static const uint8_t kPinData = 4;
static const uint8_t kPinDigitalInput = 8;
static const uint8_t kPinOutputLatch = 6;
static const uint8_t kPinInputLatch = 7;
static const uint8_t kPinClk = 5;

// PWM/audio output.
static const uint8_t kPinDacLatch = 10;
static const uint8_t kPinVcoOut = 3;
static const uint8_t kPinVcaOut = 11;
static const uint8_t kPinVcfCutoffOut = 9;
static const uint8_t kPinVcfResonanceOut = 10;

static const uint8_t kPinAnalogInput = 0;

// ---- LCD type ---------------------------------------------------------------

static const uint8_t kLcdWidth = 16;
static const uint8_t kLcdWidthLog2 = 4;
static const uint8_t kLcdHeight = 2;

}  // namespace hardware_shruti

#endif  // HARDWARE_SHRUTI_SHRUTI_H_
