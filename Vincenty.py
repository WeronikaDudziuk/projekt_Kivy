import math as m
import numpy as np

def vincenty(latA, lonA, latB, lonB):
    fiA = np.deg2rad(latA)
    lambdaA = np.deg2rad(lonA)
    fiB = np.deg2rad(latB)
    lambdaB =  np.deg2rad(lonB)

    a = 6378137
    e2 = 0.00669438002290

    b = a*m.sqrt(1-e2)
    f = 1 - (b/a)
    dlambda = lambdaB - lambdaA
    UA = m.atan(((1-f)*m.tan(fiA)))
    UB = m.atan(((1-f)*m.tan(fiB)))

    L1 = dlambda
    L2 = 0
    i = 0
    while  m.fabs(L1 - L2) >= np.deg2rad(0.000001/3600):
        L2 = L1
        i = i + 1
        
        sins = m.sqrt((m.cos(UB)*m.sin(L2))**2+(m.cos(UA)*m.sin(UB)-m.sin(UA)*m.cos(UB)*m.cos(L2))**2)
        coss = m.sin(UA)*m.sin(UB)+m.cos(UA)*m.cos(UB)*m.cos(L2)
        sig = m.atan2(sins,coss)
        sina = (m.cos(UA)*m.cos(UB)*m.sin(L2))/sins
        cos2a = 1 - ((sina)**2)
        cos2sm = coss - 2*(m.sin(UA)*m.sin(UB)/cos2a)
        C = (f/16)*cos2a*(4+f*(4-3*cos2a))
        L1 = dlambda + (1-C)*f*sina*(sig+C*sins*(cos2sm + C*coss*(-1 +2*cos2sm**2)))
        
    u2 = ((a**2)-(b**2))*cos2a/(b**2)
    A = 1 + (u2/16384)*(4096 + u2*(-768 + u2*(320-175*u2)))
    B = (u2/1024)*(256 + u2*(-128+u2*(74-47*u2)))
    dsig = B*sins*(cos2sm + 0.25*B*(coss*(-1+2*(cos2sm)**2)-(1/6)*B*cos2sm*(-3+4*(sins)**2)*(-3+4*(cos2sm)**2)))
    SAB = b*A*(sig-dsig)
    return SAB


if __name__ == '__main__':
    print(vincenty(100, 21, 51, 21))
    print(np.deg2rad(0.000001/3600))