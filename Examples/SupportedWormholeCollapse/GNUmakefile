GRTECLYN_HOME = $(realpath ../..)

include $(GRTECLYN_HOME)/Tools/GNUMake/Make.defaults

# We use particles for the puncture tracking
USE_PARTICLES = TRUE

AMREX_HOME ?= $(realpath ../../../amrex)

include $(AMREX_HOME)/Tools/GNUMake/Make.defs

include ./Make.package
include $(AMREX_HOME)/Src/Base/Make.package
include $(AMREX_HOME)/Src/Boundary/Make.package
include $(AMREX_HOME)/Src/AmrCore/Make.package
include $(AMREX_HOME)/Src/Amr/Make.package
include $(AMREX_HOME)/Src/Particle/Make.package

GRTECLYN_HOME = $(realpath ../..)
GRTECLYN_SOURCE = $(GRTECLYN_HOME)/Source

src_dirs := $(GRTECLYN_SOURCE)/BlackHoles \
            $(GRTECLYN_SOURCE)/CCZ4 \
            $(GRTECLYN_SOURCE)/Matter \
            $(GRTECLYN_SOURCE)/Grids \
            $(GRTECLYN_SOURCE)/GRTeclynCore \
            $(GRTECLYN_SOURCE)/IO \
            $(GRTECLYN_SOURCE)/Maths \
            $(GRTECLYN_SOURCE)/ParticleInterpolator \
            $(GRTECLYN_SOURCE)/Tagging \
            $(GRTECLYN_SOURCE)/Wormholes


# The example's own Make.package (included above) fills GRTECLYN_CEXE_*;
# Source/ dirs no longer carry Make.package files, so glob them instead
# (same scheme as the upstream examples).
CEXE_sources += $(GRTECLYN_CEXE_sources)
CEXE_headers += $(GRTECLYN_CEXE_headers)
CEXE_sources += $(notdir $(foreach dir, $(src_dirs), $(wildcard $(dir)/*.cpp)))
CEXE_headers += $(notdir $(foreach dir, $(src_dirs), $(wildcard $(dir)/*.hpp)))
VPATH_LOCATIONS += $(src_dirs)
INCLUDE_LOCATIONS += $(realpath .) $(src_dirs) $(GRTECLYN_HOME)/Tests/CCZ4RHSTest

include $(GRTECLYN_HOME)/Tools/GNUMake/Make.rules