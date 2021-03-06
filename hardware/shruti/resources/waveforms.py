#!/usr/bin/python2.5
#
# Copyright 2009 Emilie Gillet.
#
# Author: Emilie Gillet (emilie.o.gillet@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# -----------------------------------------------------------------------------
#
# Waveform definitions.

import numpy

"""----------------------------------------------------------------------------
Waveforms for vowel synthesis
----------------------------------------------------------------------------"""

SAMPLE_RATE = 31250.0

waveforms = []
# Create amplitude modulated sine/square tables for formants.
sine_samples = []
square_samples = []
sine = numpy.sin(numpy.arange(16.0) / 16.0 * 2 * numpy.pi)
for i, x in enumerate(sine):
  gains = numpy.exp(0.184 * numpy.arange(16.0))
  gains[0] = 0
  values = gains * x * 4
  values = numpy.round(values).astype(int)
  amps = numpy.round(gains)
  if (i >= 8):
    amps = -amps
  square_samples.extend(amps.astype(int))
  sine_samples.extend(values)

waveforms.extend([
    ('formant_sine', sine_samples),
    ('formant_square', square_samples)
])


"""----------------------------------------------------------------------------
Band-limited waveforms
----------------------------------------------------------------------------"""

WAVETABLE_SIZE = 256

# The Juno-6 / Juno-60 waveforms have a brighter harmonic content, which can be
# recreated by adding to the signal a 1-pole high-pass filtered version of
# itself.
JUNINESS = 1.0


# If you look at the bandlimited waveform produced by the approach described
# in the BLIT paper, you'll find that they are not causal: it is as if the
# band-limiting filter "anticipated" the discontinuity and started the
# oscillations/ringing to smooth the discontinuity *before* it happens.
# Such things do not exist in nature.
# A way of avoiding this is to use a causal version of the band-limiting filter,
# obtained by minimum phase reconstruction of the sinc. It doesn't sound better.
CAUSAL = False


def Scale(array, min=0, max=255, center=True):
  if center:
    array -= array.mean()
  mx = numpy.abs(array).max()
  array = (array + mx) / (2 * mx)
  array = array * (max - min) + min
  return numpy.round(array).astype(int)


def MinimumPhaseReconstruction(signal, fft_size=16384):
  Xf = numpy.fft.fft(signal, fft_size)
  real_cepstrum = numpy.fft.ifft(numpy.log(numpy.abs(Xf))).real
  real_cepstrum[1:fft_size / 2] *= 2
  real_cepstrum[fft_size / 2 + 1:] = 0
  min_phi = numpy.fft.ifft(numpy.exp(numpy.fft.fft(real_cepstrum))).real
  return min_phi


# Sine wave.
numpy.random.seed(21)
sine = -numpy.sin(numpy.arange(WAVETABLE_SIZE + 1) / float(WAVETABLE_SIZE) * 2 * numpy.pi) * 127.5 + 127.5
sine += numpy.random.rand(WAVETABLE_SIZE + 1) - 0.5

# Band limited waveforms.
num_zones = (107 - 24) / 16 + 2
bl_pulse_tables = []
bl_square_tables = []
bl_saw_tables = []
bl_tri_tables = []

wrap = numpy.fmod(numpy.arange(WAVETABLE_SIZE + 1) + WAVETABLE_SIZE / 2, WAVETABLE_SIZE)
quadrature = numpy.fmod(numpy.arange(WAVETABLE_SIZE + 1) + WAVETABLE_SIZE / 4, WAVETABLE_SIZE)
fill = numpy.fmod(numpy.arange(WAVETABLE_SIZE + 1), WAVETABLE_SIZE)

if CAUSAL:
  window = numpy.hanning(WAVETABLE_SIZE)
else:
  window = 1


for zone in range(num_zones):
  f0 = 440.0 * 2.0 ** ((24 + 16 * zone - 69) / 12.0)
  period = SAMPLE_RATE / f0
  m = 2 * numpy.floor(period / 2) + 1.0
  i = numpy.arange(-WAVETABLE_SIZE / 2, WAVETABLE_SIZE / 2) / float(WAVETABLE_SIZE)
  pulse = numpy.sin(numpy.pi * i * m) / (m * numpy.sin(numpy.pi * i) + 1e-9)
  pulse[WAVETABLE_SIZE / 2] = 1.0
  pulse *= window
  if CAUSAL:
    pulse = MinimumPhaseReconstruction(pulse)[:(WAVETABLE_SIZE + 1)]
  else:
    pulse = pulse[fill]

  square = numpy.cumsum(pulse - pulse[wrap])
  triangle = -numpy.cumsum(square[::-1] - square.mean()) / WAVETABLE_SIZE

  square -= JUNINESS * triangle
  if zone == num_zones - 1:
    square = sine
  bl_square_tables.append(('bandlimited_square_%d' % zone,
                          Scale(square[quadrature])))
  
  triangle = triangle[quadrature]
  if zone == num_zones - 1:
    triangle = sine
  bl_tri_tables.append(('bandlimited_triangle_%d' % zone,
                        Scale(triangle[quadrature])))

  saw = -numpy.cumsum(pulse[wrap] - pulse.mean())
  saw -= JUNINESS * numpy.cumsum(saw - saw.mean()) / WAVETABLE_SIZE
  if zone == num_zones - 1:
    saw = sine
  bl_saw_tables.append(('bandlimited_saw_%d' % zone,
                       Scale(saw[quadrature])))

waveforms.extend(bl_square_tables)
waveforms.extend(bl_saw_tables)
waveforms.extend(bl_tri_tables)


def LoadWavetable(x):
  # Load the data and split/pad single cycle waveforms.
  array = numpy.array(map(ord, list(file(x).read())))
  cycle = 256 if len(array) == 4096 else 128
  num_cycles = len(array) / cycle
  assert num_cycles == 16
  wavetable = numpy.zeros((num_cycles, cycle + 1))
  for i in xrange(num_cycles):
    for j in xrange(cycle):
      wavetable[i, j] = array[i * cycle + j]
    wavetable[i, cycle] = wavetable[i, 0]
  return wavetable.ravel()


waveforms.append((
    'wavetable',
    LoadWavetable('hardware/shruti/data/wavetable.bin')))


"""----------------------------------------------------------------------------
Vowel data (formant amplitudes)
-----------------------------------------------------------------------------"""

vowel_data = [
27, 40,  89, 253, 16,
18, 51,  62, 220, 96,
15, 69,  93, 236, 112,
10, 84, 110, 218, 128,
23, 44,  87, 252, 16,
13, 29,  80, 216, 0,
 6, 46,  81, 195, 0,
 9, 51,  95, 243, 3,
 6, 73,  99, 122, 233]

waveforms.append(('vowel_data', vowel_data))
