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

// phi and Pi both asymptote to zero.  For the rotating Ellis-Bronnikov data
// this holds only because the background generator subtracts the scalar's
// outer-end asymptote phi(eta -> +infinity) before writing the table; the
// inner end (the compactified far universe at r -> 0) carries a nonzero
// constant, but that end never touches the outer boundary where the
// Sommerfeld condition reads these values.
static const std::array<amrex::Real, 2> additional_asymptotic_values{};
static const std::array<amrex::Real, NUM_VARS> asymptotic_values =
    ArrayTools::concatenate(CCZ4StateVariables::asymptotic_values,
                            additional_asymptotic_values);
} // namespace StateVariables

#endif /* STATEVARIABLES_HPP */
