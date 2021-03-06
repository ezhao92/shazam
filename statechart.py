import time, math
#import cwiid

#State Constants
YAW_TRACK = 1
YAW_STAY = 2
PITCH_TRACK = 3
PITCH_STAY = 4

#LED Configuration Params
l_12 = 2
l_23 = 4
l = l_12 + l_23
h = 2

pitch_state = 0
yaw_state = 0
max_threshold_s = 45*math.pi/180
min_threshold_s = 5*math.pi/180
max_threshold_t = max_threshold_s * .5
min_threshold_t = min_threshold_s * .5

#wiimote = cwiid.Wiimote("")
user = {'x' : 0, 'y': 0, 'z': 0, 'roll': 0, 'pitch': 0, 'yaw': 0}
wii = {'x' : 0, 'y': 0, 'z': 1, 'roll': 0, 'pitch': 0, 'yaw': 0}
lamp = {'x' : 1, 'y': 0, 'z': 1, 'roll': 0, 'pitch': 0, 'yaw': 0}

"""
Read HID data from WiiMote and return list points of infrared positions
"""
def getData():
    temp_points = [] #Unordered point data
    point1, point2, point3, point4 = 0, 0, 0, 0
    distances = {}
    #Grab relevant data from Wii and put in temp_points
    messages = wiimote.get_mesg()   # Get Wiimote messages
 
    for mesg in messages:   # Loop through Wiimote Messages
        if mesg[0] == cwiid.MESG_IR: # If message is IR data
            if rec_flg == 1:    # If recording
                for s in mesg[1]:   # Loop through IR LED sources
                    if s:   # If a source exists
                        temp_points.append(s['pos'])
                         
    if len(temp_points) != 4:
        print ('Invalid temp point length %d' %temp_points)
        return None
                             
    #Calculate respective distances for all pairs of points and put in distances dictionary
    distances = getDistances(temp_points)
    #Indices of min pair of points
    indexA, indexB = min(distances, key=distances.get)
    #Find point1 and point2 based on indexA and indexB
    point1, point2, point3, point4 = findPoints(temp_points, indexA, indexB)

    return [temp_points[point1], temp_points[point2], temp_points[point3], temp_points[point4]]

"""
Calculate all distances of points in list points and returns dictionary of form
    {(pointA, pointB): distance}
"""
def getDistances(points):
    distances = {}
    for i in range(0, len(points)):
        for j in range(0, len(points)):
            if i != j:
                distances[(i, j)] = compute_distance(points[i], points[j])
            else:
                distances[(i, j)] = float('inf')
    return distances

"""
Given temp_points, and indexA and indexB, find 
point1, point2, point3, and point4
"""

def findPoints(temp_points, indexA, indexB):
    point1, point2, point3, point4 = 0, 0, 0, 0
    indexC = 0
    for i in range(0, len(temp_points)):
        if i != indexA and i!= indexB:
            indexC = i
            break
    
    distanceA = distances[(indexA, indexC)]
    distanceB = distances[(indexB, indexC)]
    if distanceA > distanceB:
        point1 = indexA
        point2 = indexB
    else:
        point1 = indexB
        point2 = indexA

    #Find point3 and point4 based on indexC and indexD
    indexD = 6 - (indexA + indexB + indexC)
    if temp_points[indexC][1] <= temp_points[indexD][1]
        point3 = indexC
        point4 = indexD
    else:
        point3 = indexD
        point4 = indexC
    return point1, point2, point3, point4


"""
Populates user dictionary with user's x, y, z position
and pitch and roll
"""
def update_userData(points):
    psi1, psi2, psi3 = points[0][0], points[1][0], points[2][0]
    theta3, theta4 = points[2][1], points[3][1]
    c = (l_23/l) * (math.tan(psi1)-math.tan(psi3))/(math.tan(psi2)-math.tan(ps3))
    a = 1 - c
    b = math.tan(psi1) - (math.tan(psi2) * c)

    psi_u = math.atan2(-a, b)
    x_u = (l * (math.cos(psi_u) + math.sin(psi_u) * (math.tan(psi1) - .5)))/(math.tan(psi1) - math.tan(psi3))
    y_u = x_u * math.tan(psi_u)
    z_u = (x_u + l/2 * math.sin(psi_u)) * math.tan(theta3)

    z3 = z_u
    x3 = (x_u + l/2 * math.sin(psi_u))
    r3 = math.sqrt(x3*x3 + z3*z3)
    theta_prime = abs(theta4-theta3)
    h_prime = r3 * math.sin(theta_prime)
    alpha = 90 - theta3
    beta = 90 - theta_prime
    gamma = math.acos(h_prime/h)
    theta_u = -180 + alpha + beta + gamma

    user['x'], user['y'], user['z'] = x_u, y_u, z_u
    user['yaw'], user['pitch'] = psi_u, theta_u


"""
Calculate desired pitch and yaw based off of user and lamp data
"""
def calculate_CommandedPitchandYaw():
    # Spot offset from user
    rOff = user['z']/math.tan(user['pitch']) * (-1)
    xOff = rOff * math.cos(user['yaw']) * (-1)
    yOff = rOff * math.sin(user['yaw'])

    #Spot position in Global frame
    xSpot = user['x'] + xOff
    ySpot = user['y'] + yOff

    #Spot offset from Lamp
    xOffL = xSpot - lamp['x']
    yOffL = ySpot - lamp['y']
    rOffL = math.sqrt(xOffL*xOffL + yOffL*yOffL)

    #Lamp Pitch and Yaw commands
    lampPitch = math.atan2(lamp['z'], rOffL)
    lampYaw = math.atan2(yOffL, xOffL)

    print ('xSpot - %f, ySpot - %f, lampPitch - %f, lampYaw - %f' %(xSpot, ySpot, lampPitch*(180/math.pi), lampYaw*(180/math.pi)))
    return lampPitch, lampYaw

    
"""
Compute distances between p1, p2 using distance formula
"""
def compute_distance(p1, p2):
    x = p1[0]-p2[0]
    y = p1[1]-p2[1]
    return math.sqrt(math.pow(x, 2) + math.pow(y, 2))

"""
Zero Out Motors
"""
def calibrate():
    pass

"""
Performs state transitions, motor control
"""
def stateChart():
    points = getData()
    #Returns sorted points list. If None, means invalid data
    if points == None:
        return

    update_userData(points)

    com_pitch, com_yaw = calculate_CommandedPitchandYaw()
    pitch_diff = abs(com_pitch - lamp['pitch'])
    yaw_diff = abs(com_yaw - lamp['yaw'])

    #State transition logic
    if yaw_state == YAW_STAY:
        if yaw_diff > min_threshold_s or yaw_diff < max_threshold_s:
            yaw_state = YAW_TRACK
        else:
            yaw_state = YAW_STAY
    if yaw_state == YAW_TRACK:
        if yaw_diff > min_threshold_t or yaw_diff < max_threshold_t:
            yaw_state = YAW_TRACK
        else:
            yaw_state = YAW_STAY
    
    if pitch_state == PITCH_STAY:
        if pitch_diff > min_threshold_s or pitch_diff < max_threshold_s:
            pitch_state = PITCH_TRACK
        else:
            pitch_state = PITCH_STAY
    if pitch_state == PITCH_TRACK:
        if pitch_diff > min_threshold_t or pitch_diff < max_threshold_t:
            pitch_state = PITCH_TRACK
        else:
            pitch_state = PITCH_STAY


    #State Action logic. Command motors
    if yaw_state == YAW_STAY:
        pass
    elif yaw_state == YAW_TRACK:
        #Send commanded yaw angle
        pass
    if pitch_state == PITCH_STAY:
        pass
    elif pitch_state == PITCH_TRACK:
        #Send commanded pitch angle
        pass

"""
Main execution block
"""
wiimote.enable(cwiid.FLAG_MESG_IFC)
wiimote.rpt_mode = cwiid.RPT_IR | cwiid.RPT_BTN
calibrate()
while True:
    stateChart()
    time.sleep(1)
