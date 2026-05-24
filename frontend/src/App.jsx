import { useState } from 'react'
import {Route, Routes} from 'react-router-dom'
import Home from '../pages/Home'
import MonyAI from '../pages/MonyAI'
import Profile from '../pages/Profile'
import ForgotPassword from '../pages/ForgotPassword'
import ResetPassword from '../pages/ResetPassword'
import { Toaster } from 'react-hot-toast'


function App() {


  return (
    <>

    <Toaster position="top-right" toastOptions={{
      duration: 8000,
      style:{
        fontSize: '25px'

      }
    }} />
    <Routes>
      <Route path="/" element={<Home />}/>
      <Route path="/monyai" element={<MonyAI />}/>
      <Route path="/profile" element={<Profile />}/>
      <Route path="/forgot-password" element={<ForgotPassword />}/>
      <Route path="/reset-password" element={<ResetPassword />}/>
    </Routes>

      
    </>
  )
}

export default App
