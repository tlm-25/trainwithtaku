import {useState} from 'react'

import { Link } from 'react-router-dom'
function Navigation(props){
        //children refers to everything inside the opening and closing tags of layout in app.jsx
        //children components rendered in between curly brackets 
        //children constant which refers to the propls - props referenced with curly brackets 
        const {children} = props
        const [showModal, setShowModal] = useState(false)
    
        //when the screen is small, managing state of displaying options
        const [showSmallScreenNavOptions, setShowSmallScreenNavOptions] = useState(false)
        

        //
    
        
        function handleSmallScreenMenu(){
            //toggle showSmallScreenNavOptions - i.e. display or hide the menu depending on current state
            setShowSmallScreenNavOptions(!showSmallScreenNavOptions)
    
        }
    

            return (<>
                        
                
            
                        <nav className='navbar'>
                            
                            <div className="logo-section">
                                <img className="twt-logo" src="/twt-logo.png" alt="TWT logo"></img>
                                
                            </div>

                            <a href='#' className={'hamburger-menu-button'+ (showSmallScreenNavOptions ? " clicked" : " ")} onClick={handleSmallScreenMenu}>
                                <span className="bar"></span>
                                <span className="bar"></span>
                                <span className="bar"></span>
                            </a>

                            {
                            
                            (<div className={'navbar-links'+ (showSmallScreenNavOptions ? " active" : " ")}>
                                
                                <ul>
                                    <li><Link to="/" className="nav-link">Home</Link></li>
                                    <li><Link to="#" className="nav-link">About</Link></li>
                                    <li><Link to="#" className="nav-link">Shop</Link></li>
                                    <li><Link to="#" className="nav-link">Blog</Link></li>
                                    <li><Link to="#" className="nav-link">Contact</Link></li>
                                    <li><Link to="/monyai" className="nav-link"> MonyAI</Link></li>
                                    <li><Link to="#" className="nav-link"> Stats</Link></li>
                                    <div></div>
                                </ul>
                                

                            </div>)}




                            
                    
                    </nav>
                </>)


}

export default Navigation;