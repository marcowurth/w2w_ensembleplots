
import numpy as np

Cp = 1004.5;
Cv = 717.5;
Rd = 287.04;
Rv = 461.6;
c  = (Rv/Rd-1);
RvRd = Rv / Rd;
g = 9.80665;
L = 2.50e6;
Lf = 3.34*10**5;
Talt = 288.1500;
Tfrez = 273.1500;
To = 300.;
Po = 101325.;
Pr = 1000.;
lapsesta = 6.5 / 1000.;
kappa = Rd / Cp;
epsil = Rd/Rv;
pi = np.pi;
pid = pi/180.;
R_earth = 6371200.;
omeg_e = (2.*pi) / (24.*3600.);
eo = 6.112;
missval = -9999.;
eps = 2.2204e-16

def calc_es(temp):
    ''' Compute saturated vapor pressure for -30C<T<35C '''
    ''' temp: Input temperature '''
    ''' Output: saturated vapor pressure in hPa '''
    return eo * np.exp(17.67 * (temp - Tfrez) / (temp - Tfrez + 243.5))

def calc_rh(temp, qv, p):
    ''' Compute relative humidity '''
    ''' temp: Input temperature in K '''
    ''' qv: Input specific humidity '''
    ''' p: Input pressure in Pa '''
    rh = 1e2 * calc_mr(qv) / calc_mrs(temp, p)
    return rh

def calc_mr(qv):
    ''' Compute humidity mixing ratio '''
    ''' Input: specific humidity '''
    ''' Output: mixing ratio in kg/kg '''
    return qv / (1 - qv)

def calc_mrs(temp, p):
    ''' Compute saturated mixing ratio for -30C<T<35C '''
    ''' temp: Input temperature in K '''
    ''' p: Input pressure in hPa '''
    ''' mrs: Output saturated mixing ratio in kg/kg '''
    return epsil * calc_es(temp) / p

def calc_the_from_qv(temp, qv, p):
    ''' Compute equivalent potential temperature in K after Bolton (1980, MWR)'''
    ''' temp: Input temperature in K '''
    ''' qv: Input specific humidity '''
    ''' p: Input pressure in hPa '''  
    r = calc_mr(qv)
    thexact = temp * (1000 / p) ** (kappa * (1 - 0.28 * r))
    T_l = 1 / (1 / (temp - 55) - np.log(calc_rh(temp, qv, p) / 100) / 2840) + 55
    return thexact * np.exp((3.376 / T_l - 0.00254) * 1.e3 * r * (1 + 0.81 * r))

def calc_the_from_relhum(rh, temp, p):
    ''' temp: Input temperature in K '''
    ''' rh: relative humidity in % '''
    ''' p: Input pressure in hPa '''  
    r = calc_mr_from_rh(rh, temp, 850)
    thexact = temp * (1000 / p) ** (kappa * (1 - 0.28 * r))
    T_l = 1 / (1 / (temp - 55) - np.log(rh / 100) / 2840) + 55
    return thexact * np.exp((3.376 / T_l - 0.00254) * 1.e3 * r * (1 + 0.81 * r))

def calc_mfl(qv, u, v):
    ''' Compute moisture transport'''
    ''' qv: Input specific humidity '''
    ''' u: Input zonal wind '''
    ''' v: Input meridional wind '''
    mfl = np.sqrt((u*qv)**2. + (v*qv)**2.)
    return mfl

def calc_vint(var, p):
    ''' Compute vertical integral '''
    ''' '''
    ''' var: Arbitrary input variable '''
    ''' p: pressure in Pa '''

    varvint = np.zeros([var.shape[1], var.shape[2]])
    varvint = varvint + var[ 0, :, :]*(p[ 0]-p[ 1])
    varvint = varvint + var[-1, :, :]*(p[-2]-p[-1])
    for k in range(1, var.shape[0]-1):
        varvint = varvint + var[k, :, :]*0.5*(p[k-1]-p[k+1])

    return varvint

def calc_mr_from_rh(rh, temp, p):
    ''' Compute mixing ratio from relative humidity '''
    ''' rh: relative humidity in % '''
    ''' temp: Input temperature in K '''
    ''' p: Input pressure in hPa '''
    ''' Formula from Hobbs 1977, p. 74 '''
    return 1e-2 * rh * calc_mrs(temp, p)
    
def calc_qv_from_mr(mr):
   ''' Compute specific humidity from mixing ratio '''
   ''' mr is mixing ratio '''
   ''' Formula from Salby 1996, p. 118 '''
   return mr / (1 + mr)