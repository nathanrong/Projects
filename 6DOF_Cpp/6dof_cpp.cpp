// Start of Project
#include <iostream>
#include <cmath>
#include <functional>
#include <stdexcept>
#include <vector>
#include <algorithm>

struct envVars
{
    double altitude; // ft, positive value for env calcs
    double airspeed; // ft/s
    double temperature; // Rankine    
    double pressure; // lb/ft^2
    double density; // slugs/ft^3
    double viscosity;
    double reynolds; 
};

struct bodyVel {
    double u;  // ft/s
    double v; // ft/s
    double w; // ft/s
};

struct bodyAcc {
    double udot; // ft/s^2
    double vdot; // ft/s^2
    double wdot; // ft/s^2
};

struct inertialVel {
    double NorthSouth; // ft/s
    double EastWest; // ft/s
    double Vertical; // ft/s
};

struct inertialPos {
    double norsou; // ft
    double estwst; // ft
    double altitude; // ft, negative up convention
};

struct translational {
    bodyVel bodyvel; 
    bodyAcc bodyacc; 
    inertialVel inertvel; 
    inertialPos inertpos;
};

struct angles {
    double alpha; // rad
    double beta; // rad
    double alphadot; // rad/s
    double betadot; // rad/s
};

void envCalculate(double cbar, envVars& env, translational& transl, angles& ang)
{
    const double tropopause_alt = 36089.0;
    const double gravity = 32.174;
    const double gas_const = 1716;
    const double suth = 198.6; // Sutherland's Constant

    env.altitude = std::abs(transl.inertpos.altitude);
    const double earth_radius = 20900000.0;
    const double geopot_alt = (earth_radius / (earth_radius + env.altitude) * env.altitude);

    env.airspeed = std::sqrt(transl.bodyvel.u*transl.bodyvel.u + transl.bodyvel.v*transl.bodyvel.v + transl.bodyvel.w*transl.bodyvel.w);
    ang.alpha = std::atan2(transl.bodyvel.w, transl.bodyvel.u);
    ang.beta = std::asin(transl.bodyvel.v / env.airspeed);
    ang.alphadot = (transl.bodyvel.u * transl.bodyacc.wdot - transl.bodyvel.w * transl.bodyacc.udot) / (transl.bodyvel.u * transl.bodyvel.u + transl.bodyvel.w * transl.bodyvel.w);
    double airspd_dot = (transl.bodyvel.u * transl.bodyacc.udot + transl.bodyvel.v * transl.bodyacc.vdot + transl.bodyvel.w * transl.bodyacc.wdot) / env.airspeed;
    ang.betadot = (env.airspeed * transl.bodyacc.vdot - airspd_dot * transl.bodyvel.v) / (std::sqrt(env.airspeed * env.airspeed - transl.bodyvel.v * transl.bodyvel.v) * env.airspeed);

    const double diff = geopot_alt - tropopause_alt;
    if (diff > 0) {
        env.temperature = 389.99;
        const double tropo_P = 472.68;
        const double tropo_rho = 0.0007038;
        env.pressure = tropo_P * std::exp(-gravity * diff / (gas_const * env.temperature));
        env.density = tropo_rho * std::exp(-gravity * diff / (gas_const * env.temperature));
        env.viscosity = 2.27 * 1e-8 * std::pow(env.temperature, 1.5) / (env.temperature + suth);
    } else {
        const double lapse_rate = -0.003566;
        const double SL_T = 518.69;
        const double SL_P = 2116.2;
        const double SL_rho = 0.002377;
        env.temperature = SL_T + lapse_rate * geopot_alt;
        env.pressure = SL_P * std::pow((env.temperature / SL_T), (-gravity / (gas_const * lapse_rate)));
        env.density = SL_rho * std::pow((env.temperature / SL_T), (-gravity / (gas_const * lapse_rate) - 1));
        env.viscosity = 2.27 * 1e-8 * std::pow(env.temperature, 1.5) / (env.temperature + suth);
    }
    env.reynolds = env.density * cbar * env.airspeed / env.viscosity;
}

std::vector<double> operator+(const std::vector<double>& v1, const std::vector<double>& v2) {
    if (v1.size() != v2.size()) {
        throw std::invalid_argument("Vector sizes don't match");
    }
    std::vector<double> result(v1.size());
    for (size_t i=0; i < v1.size(); ++i) {
        result[i] = v1[i] + v2[i];
    }
    return result;
}

std::vector<double> operator*(double scalar, const std::vector<double>& v) {
    std::vector<double> result(v.size());
    for (size_t i=0; i < v.size(); ++i) {
        result[i] = scalar * v[i];
    }
    return result;
}

std::vector<double> rk4Step(const std::vector<double>& state, double dt, const std::function<std::vector<double>(const std::vector<double>&)>& f)
{
    std::vector<double> k1 = f(state);
    std::vector<double> k2 = f(state + 0.5 * dt * k1);
    std::vector<double> k3 = f(state + 0.5 * dt * k2);
    std::vector<double> k4 = f(state + dt * k3);
    return state + (dt/6) * (k1 + 2*k2 + 2*k3 + k4);
}

class Actuator {
    public:
        // Make virtual so the destructor so both are deleted
        virtual ~Actuator() = default;

        // Member function in base class that can be overridden in child class
        virtual void step(double dt, double command) = 0;

        virtual double state() const = 0;
};

class FirstOrderActuator : public Actuator {
    public:
        FirstOrderActuator(double tau, double init_state)
            : tau_(tau), state_(init_state) {}

        void step(double dt, double command) override {
            auto derivative = [this, command](const std::vector<double>& state) {
                return std::vector<double> {
                    (command - state[0]) / tau_
                };
            };
            state_ = rk4Step({state_}, dt, derivative)[0];
        }
        double state() const override {
            return state_;
        }
    
    private:
        double tau_;
        double state_;
};

class SecondOrderActuator : public Actuator {
    public:
        SecondOrderActuator(double wn, double zeta, double init_pos, double init_vel)
            : wn_(wn), zeta_(zeta), state_{init_pos, init_vel} {}

        void step(double dt, double command) override {
            auto derivative = [this, command](const std::vector<double>& state) {
                return std::vector<double> {
                    state[1], wn_ * wn_ * (command - state[0]) - 2.0 * zeta_ * wn_ * state[1]
                };
            };
            state_ = rk4Step(state_, dt, derivative);
        }
        double state() const override {
            return state_[0];
        }

        double velocity() const {
            return state_[1];
        }
    
    private:
        double wn_;
        double zeta_;
        std::vector<double> state_;
};

double saturation_limits(double limit_min, double limit_max, double value) {
    if (limit_min > limit_max) {
        throw std::invalid_argument("Minimum exceeds maximum saturation value...");
    }
    return std::clamp(value, limit_min, limit_max);
}

int main()
{
    // Actuator saturation limits in radians
    // calculate pi in runtime
    const double pi = std::acos(-1.0);
    const double deg2rad = pi / 180;
    const double elevator_min = -30.0 * deg2rad;
    const double elevator_max = 30.0 * deg2rad;

    // auto [h, T, P, rho, viscosity, RE] = envCalculate(20000.0, 5.5, 250.0);
    // std::cout << "--- Atmospheric Conditions at 20k feet ---\n";
    // std::cout << "Altitude:     " << h << " ft\n";    
    // std::cout << "Temperature:  " << T << " R\n";
    // std::cout << "Pressure:     " << P << " psf\n";
    // std::cout << "Density:      " << rho << " slugs/ft^3\n";
    // std::cout << "Viscosity:    " << viscosity << "\n";
    // std::cout << "Reynolds Num: " << RE << "\n";
    std::vector<double> state(2, 0.0);
    double dt = 0.1;
    double time = 0.0;
    // double tau = 0.3;
    double wn = 2;
    double zeta = 1;

    // Actuators
    FirstOrderActuator elevator(0.3, 0.0);
    SecondOrderActuator horiz_stab(0.3, 1.0, 0.0, 0.0);
    FirstOrderActuator aileron(0.3, 0.0);
    FirstOrderActuator rudder(0.5, 0.0);
    SecondOrderActuator throttle(1.0, 1.0, 0.0, 0.0);

    const double command_deg = 25.0;
    const double command = command_deg * deg2rad;

    const double sim_time = 5.0;
    const double tolerance = 0.001 * deg2rad;
    const int max_steps = 10000;

    for (int step = 0; step < max_steps; ++step) {
        const double time = step * dt;
        const double saturated_command = 
            saturation_limits(elevator_min, elevator_max, command);
        
        elevator.step(dt, saturated_command);
        const double error = std::abs(saturated_command - elevator.state());

        std::cout << "t = " << time + dt
                << ", command = " << saturated_command / deg2rad
                << " deg, elevator = " << elevator.state() / deg2rad
                << " deg\n";

        if (error < tolerance) {
            std::cout << "Actuator converged...\n";
            break;
        }

    }

    return 0;
    // Need to do:
    // Fix zero airspeed cases
    // fix void for envCalc -> needs to be the struct name(s)
    // remove return
}