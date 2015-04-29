#!/usr/bin/env python

import numpy as np
from scipy.integrate import ode
import matplotlib.pyplot as plt
from matplotlib import animation

class ThetaAnim(object):

    def __init__(self, figure, times, theta, skip):
        axes = figure.add_axes([0.1, 0.1, 0.8, 0.8])
        axes.set_xlim(np.min(times), np.max(times))
        axes.set_ylim(np.min(thetas), np.max(thetas))
        self._line, = axes.plot([], [])
        self._times = times
        self._thetas = thetas
        self._skip = skip

    def create_init(self):
        def init():
            self._line.set_data([], [])
            return self._line
        return init

    def create_animate(self):
        def animate(i):
            t = i*self._skip
            self._line.set_data(self._times[:t], self._thetas[:t])
            return self._line
        return animate


def func(t, y, g, l, q, F_d, omega_d):
    return [
        y[1],
        -(g/l)*y[0] - q*y[1] + F_d*np.sin(2.0*np.pi*omega_d*t)
    ]

def jacobian(t, y, g, l, q, F_d, omega_d):
    return [
        [0.0, 1.0],
        [-g/l, -q]
    ]

def solve(func, jac, t0=0.0, t_max=20.0, delta_t=0.01,
          theta0=0.1, omega0=0.0, params={'g': 9.81, 'l': 9.81,
                                          'q': 0.05}):
# select integrator
    integrator = ode(func, jac).set_integrator('dopri5')
# set initial values
    integrator.set_initial_value([theta0, omega0], t0)
# set parameters
    integrator.set_f_params(params['g'], params['l'], params['q'],
                            params['F_d'], params['omega_d'])
    integrator.set_jac_params(params['g'], params['l'], params['q'])
# solve equations
    times = [t0]
    thetas = [theta0]
    omegas = [omega0]
    while integrator.successful() and integrator.t < t_max:
        integrator.integrate(integrator.t + delta_t)
        times.append(integrator.t)
        thetas.append(integrator.y[0])
        omegas.append(integrator.y[1])
    return times, thetas, omegas

def plot_solution(times, thetas, omegas):
    plt.subplot(3, 1, 1)
    plt.plot(times, thetas)
    plt.subplot(3, 1, 2)
    plt.plot(times, omegas)
    plt.subplot(3, 1, 3)
    plt.plot(thetas, omegas)
    plt.show()

def animate_solution(mp4_file, times, thetas, omegas, skip):
    figure = plt.figure()
    thetaAnim = ThetaAnim(figure, times, thetas, skip)
    init_f = thetaAnim.create_init()
    anim_f = thetaAnim.create_animate()
    anim = animation.FuncAnimation(figure, anim_f, init_func=init_f,
                                   frames=len(times)/skip, interval=1,
                                   blit=True)
    anim.save(mp4_file, fps=15, writer=animation.AVConvFileWriter())

if __name__ == '__main__':
    from argparse import ArgumentParser
    arg_parser = ArgumentParser(description='solve ODE for a harmonic '
                                            'damped pendulum')
    arg_parser.add_argument('--l', type=float, default=9.81,
                            help='length of pendulum [m]')
    arg_parser.add_argument('--g', type=float, default=9.81,
                            help='gravitational acceleration [rad/s**2]')
    arg_parser.add_argument('--q', type=float, default=0.05,
                            help='damping factor [1/s]')
    arg_parser.add_argument('--F_d', type=float, default=0.0,
                            help='amplitude of driving force')
    arg_parser.add_argument('--omega_d', type=float, default=1.0,
                            help='frquency of driving force')
    arg_parser.add_argument('--theta0', type=float, default=0.05,
                            help='initial theta value [rad]')
    arg_parser.add_argument('--omega0', type=float, default=0.0,
                            help='initial omega value [rad/s]')
    arg_parser.add_argument('--t0', type=float, default=0.0,
                            help='initial time value [s]')
    arg_parser.add_argument('--t_max', type=float, default=10.0*2.0*np.pi,
                            help='maximum time value [s]')
    arg_parser.add_argument('--delta_t', type=float, default=0.01,
                            help='time step [s]')
    arg_parser.add_argument('--output', action='store_true',
                            help='write solutions to standrad output')
    arg_parser.add_argument('--plot', action='store_true',
                            help='make plot')
    arg_parser.add_argument('--mp4', help='create MP4 animated plot')
    arg_parser.add_argument('--skip', type=int, default=5,
                            help='number of skip points for animation')
    options = arg_parser.parse_args()
    times, thetas, omegas = solve(
            func=func, jac=jacobian,
            t0=options.t0, t_max=options.t_max, delta_t=options.delta_t,
            theta0=options.theta0, omega0=options.omega0,
            params={'g': options.g, 'l': options.l, 'q': options.q,
                    'F_d': options.F_d, 'omega_d': options.omega_d}
    )
    if options.output:
        for time, theta, omega in zip(times, thetas, omegas): 
            print '{0:.3f}\t{1:.10f}\t{2:.10f}'.format(time, theta, omega)
    if options.plot:
        plot_solution(times, thetas, omegas)
    if options.mp4:
        animate_solution(options.mp4, times, thetas, omegas, options.skip)