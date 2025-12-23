import { useState } from 'react'
import {Route, Routes} from 'react-router-dom'
import Home from '../pages/Home'
import MonyAI from '../pages/MonyAI'



function App() {


  return (
    <>

    <Routes>
      <Route path="/" element={<Home />}/>
      <Route path="/monyai" element={<MonyAI />}/>
    </Routes>

      
    </>
  )
}

export default App
