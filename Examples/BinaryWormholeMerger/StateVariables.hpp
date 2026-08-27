#ifndef STATEVARIABLES_HPP
#define STATEVARIABLES_HPP

#include "ArrayTools.hpp"
#include "CCZ4StateVariables.hpp"

enum
{
    c_phi = NUM_CCZ4_VARS,
    c_Pi,

    NUM_VARS
};

namespace StateVariables
{
static const amrex::Vector<std::string> additional_names = {"phi", "Pi"};
static const amrex::Vector<std::string> names =
    ArrayTools::concatenate(CCZ4StateVariables::names, additional_names);

static const std::array<BCParity, 2> additional_parities = {BCParity::even,
                                                            BCParity::even};
static const std::array<BCParity, NUM_VARS> parities =
    ArrayTools::concatenate(CCZ4StateVariables::parities, additional_parities);

// phi and Pi both asymptote to zero.  For the binary Ellis-Bronnikov data this
// is only true because BinaryWormholeInitialData subtracts the constant
// 2 * (1/sqrt(4 pi)) * (pi/2) that a plain sum of two atan profiles carries
// (wormhole_subtract_phi_asymptote = 1, the default).  If that switch is turned
// off, phi tends to ~0.886 instead and the Sommerfeld boundary condition will
// inject a spurious gradient at the outer boundary.
static const std::array<amrex::Real, 2> additional_asymptotic_values{};
static const std::array<amrex::Real, NUM_VARS> asymptotic_values =
    ArrayTools::concatenate(CCZ4StateVariables::asymptotic_values,
                            additional_asymptotic_values);
} // namespace StateVariables

#endif /* STATEVARIABLES_HPP */
