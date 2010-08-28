#!/usr/bin/env python

""" 
  A simple Controller GUI to drive robots and pose heads.
  Copyright (c) 2008-2010 Michael E. Ferguson.  All right reserved.

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software Foundation,
  Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import roslib; roslib.load_manifest('albany_gui')
import rospy
import wx

from geometry_msgs.msg import Twist
from sensor_msgs.msg import JointState

width = 300

class controllerGUI(wx.Frame):
    TIMER_ID = 100

    def __init__(self, parent, debug = False):  
        wx.Frame.__init__(self, parent, -1, "Controller GUI", style = wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        sizer = wx.GridBagSizer(10,10)

        # Move Base
        drive = wx.StaticBox(self, -1, 'Move Base')
        drive.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        driveBox = wx.StaticBoxSizer(drive,orient=wx.VERTICAL) 
        self.movebase = wx.Panel(self,size=(width,width-20))
        self.movebase.SetBackgroundColour('WHITE')
        self.movebase.Bind(wx.EVT_MOTION, self.onMove)  
        wx.StaticLine(self.movebase, -1, (width/2, 0), (1,width), style=wx.LI_VERTICAL)
        wx.StaticLine(self.movebase, -1, (0, width/2), (width,1))
        driveBox.Add(self.movebase)        
        sizer.Add(driveBox,(0,0),wx.GBSpan(1,1),wx.EXPAND|wx.TOP|wx.RIGHT|wx.LEFT,5)
        self.forward = 0
        self.turn = 0

        # Move Head
        head = wx.StaticBox(self, -1, 'Move Head')
        head.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        headBox = wx.StaticBoxSizer(head,orient=wx.VERTICAL) 
        headSizer = wx.GridBagSizer(5,5)
        headSizer.Add(wx.StaticText(self, -1, "Pan:"),(0,0), wx.GBSpan(1,1),wx.ALIGN_CENTER_VERTICAL)
        self.pan = wx.Slider(self, -1, 0, -100, 100, wx.DefaultPosition, (200, -1), wx.SL_HORIZONTAL | wx.SL_LABELS)
        headSizer.Add(self.pan,(0,1))
        headSizer.Add(wx.StaticText(self, -1, "Tilt:"),(1,0), wx.GBSpan(1,1),wx.ALIGN_CENTER_VERTICAL)
        self.tilt = wx.Slider(self, -1, 0, -100, 100, wx.DefaultPosition, (200, -1), wx.SL_HORIZONTAL | wx.SL_LABELS)
        headSizer.Add(self.tilt,(1,1))
        headSizer.Add(wx.StaticText(self, -1, "Tilt/Roll:"),(2,0), wx.GBSpan(1,1),wx.ALIGN_CENTER_VERTICAL)
        self.tilt2 = wx.Slider(self, -1, 0, -100, 100, wx.DefaultPosition, (200, -1), wx.SL_HORIZONTAL | wx.SL_LABELS)
        headSizer.Add(self.tilt2,(2,1))
        headBox.Add(headSizer) 
        sizer.Add(headBox, (1,0), wx.GBSpan(1,1), wx.EXPAND|wx.BOTTOM|wx.RIGHT|wx.LEFT,5)

        # timer for output
        self.timer = wx.Timer(self, self.TIMER_ID)
        self.timer.Start(100)
        wx.EVT_CLOSE(self, self.onClose)
        wx.EVT_TIMER(self, self.TIMER_ID, self.onTimer)

        self.SetSizerAndFit(sizer)
        self.Show(True)

        self.cmd_vel = rospy.Publisher('cmd_vel', Twist)
        self.cmd_joints = rospy.Publisher('cmd_joints', JointState)

    def onClose(self, event):
        self.timer.Stop()
        self.Destroy()

    def onMove(self, event=None):
        if event.LeftIsDown():        
            pt = event.GetPosition()
            self.forward = ((width/2)-pt[1])/2
            self.turn = (pt[0]-(width/2))/2           
        #else:
        #    self.forward = 0
        #    self.turn = 0
        #    pass

    def onTimer(self, event=None):
        # send joint updates
        j = JointState()
        j.name = ["head_pan", "head_tilt", "head_tilt2"]
        j.position = [self.pan.GetValue()/100.0, self.tilt.GetValue()/100.0, self.tilt2.GetValue()/100.0]
        self.cmd_joints.publish(j)
        # send base updates
        t = Twist()
        t.linear.x = self.forward/200; t.linear.y = 0; t.linear.z = 0
        t.angular.x = 0; t.angular.y = 0; t.angular.z = self.turn/200
        self.cmd_vel.publish(t)

if __name__ == '__main__':
    # initialize GUI
    rospy.init_node('controllerGUI')
    app = wx.PySimpleApp()
    frame = controllerGUI(None, True)
    app.MainLoop()
