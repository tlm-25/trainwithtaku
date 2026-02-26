import { useState } from 'react'
import {Route, Routes} from 'react-router-dom'
import Home from '../pages/Home'
import MonyAI from '../pages/MonyAI'
import Profile from '../pages/Profile'



function App() {


  return (
    <>

    <Routes>
      <Route path="/" element={<Home />}/>
      <Route path="/monyai" element={<MonyAI />}/>
      <Route path="/profile" element={<Profile />}/>
    </Routes>

      
    </>
  )
}

export default App
