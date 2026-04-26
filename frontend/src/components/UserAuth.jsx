import {useState} from 'react'
import { useAuth } from '../context/AuthContext'
import '../fanta.css'
import {toast} from 'react-hot-toast'
import {EyeInvisibleOutlined,EyeOutlined} from "@ant-design/icons"

export default function Authentication (props) {
    // props which represent a function that will open/close the pop up
    const {handleCloseModal,className} = props
    // state that checks if user is signing up (i.e. the specifically 'sign up' form)
    const [isRegistration,setIsRegistration] = useState(false)
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [confirmPassword, setConfirmPassword] = useState("")
     const [userType, setUserType] = useState("")
    const [isAuthenticating, setIsAuthenticating] = useState(false)
    const [error,setError] = useState(null)
    const [loginMessage,setLoginMessage] = useState("")
    const [signUpMessage,setSignUpMessage] = useState("")
    // state that checks if we want to show the password or not
    const [showPassword, setShowPassword] = useState(false)
    const [showConfirmPassword, setShowConfirmPassword] = useState(false)

    // Track conditions for password
    const [passwordValidation, setPasswordValidation] = useState({
        hasLowerCase: false,
        hasUpperCase: false,
        hasNumber: false,
        hasSpecialCharacters: false,
        hasEightCharacters: false
    });
    //Password check 
    const hasLowerCase = (str) => /[a-z]/.test(str);
    const hasUpperCase = (str) => /[A-Z]/.test(str);
    const hasNumber = (str) => /\d/.test(str);
    const hasEightCharacters = (str) => str.length >= 8
    const hasSpecialCharacters = (str) => /[-+_!@#$%^&*.,?]/.test(str);




    const handlePasswordChange = (e) => {
    const value = e.target.value;
    setPassword(value)
    setPasswordValidation({
        hasLowerCase: hasLowerCase(value),
        hasUpperCase: hasUpperCase(value),
        hasNumber: hasNumber(value),
        hasSpecialCharacters: hasSpecialCharacters(value),
        hasEightCharacters: hasEightCharacters(value)
            });
        };
    
    function resetUserAuthFields(){
        //reset inputs to default inputs
        const defaultValue = ""
        setLoginMessage(defaultValue)
        setPassword(defaultValue)
        setEmail(defaultValue)
        setConfirmPassword(defaultValue)
        setUserType(defaultValue)
        setShowPassword(false)
        setShowConfirmPassword(false)
        // setSignUpMessage(defaultValue)
        
        
        setPasswordValidation({
        hasLowerCase: hasLowerCase(defaultValue),
        hasUpperCase: hasUpperCase(defaultValue),
        hasNumber: hasNumber(defaultValue),
        hasSpecialCharacters: hasSpecialCharacters(defaultValue),
        hasEightCharacters: hasEightCharacters(defaultValue)
        });


    };


    


    
    //accessing signup and login actions from authcontext 
    const {signUp, login} = useAuth()

    async function handleAuthenticate () {

            //isAuthenticating is set to try while we are authenticating 
            setIsAuthenticating(true)
            setError(null)
            setLoginMessage("")
            if(isRegistration) {
                //register user
                console.log("registering user")

                //TODO - call the API for the sign up
                const signUpResponse = await signUp(email,password,userType,confirmPassword)
                
                if(signUpResponse.status === 200){
                    handleCloseModal()
                    toast.success(`Welcome to the team! Sign in and get one step closer to your goals! 💪🏾`);
                    resetUserAuthFields()

                }
                // if email already in use
                else if(signUpResponse.status === 409||signUpResponse.message.toLowerCase().includes("already")){

                    setSignUpMessage("This email already has an account associated with it. Please log in. If you have forgotten your password, you can reset it.")
                    toast.error(`An account with ${email} already exists. Please sign in or use another email.`,);

                    resetUserAuthFields()

                }


            }
            else{
                //login user
                const loginResponse = await login(email,password)
                // const data = await loginResponse.json()
                const message = loginResponse.message
                

                if(loginResponse.status === 200|| message.toLowerCase().includes("success") ){
                    //reset the inputs and close the modal once the user is logged in
                     
                    handleCloseModal()
                    toast.success(`Welcome back!💪🏾`);
                    resetUserAuthFields()
                               

                }

                else if (loginResponse.status === 401 || message.toLowerCase().includes("incorrect")){

                    setLoginMessage("Incorrect email or password")
                    toast.error(`Incorrect email or password`);


                }


                else if (loginResponse.status === 429 || message.toLowerCase().includes("too many login attempts")){
                    setLoginMessage(`${message}}`)
                    toast.error(`${message}}`)


                }


                
         

            }


            setIsAuthenticating(false)

        

    }
    //valid email address
    const emailValid = (email && /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i.test(email))

    const passwordValid = passwordValidation.hasLowerCase && passwordValidation.hasUpperCase && passwordValidation.hasSpecialCharacters && passwordValidation.hasNumber && (password==confirmPassword)



    // Check that when user signs up, password and confirm password fields are matching

    


    
    return (
        <>
        
            <div className='top-of-popup'> <h2 className="popup-title-text">{ isRegistration ? 'Sign up❚█══█❚' : 'Login❚█══█❚'} </h2><h3><button onClick={handleCloseModal}>&times;</button></h3></div>
                <p className="auth-instruction-text"><strong>{ isRegistration ? 'All requirements must be met (✅)' : 'Sign into your account'}</strong></p>
                {!isRegistration && loginMessage.toLowerCase().includes("incorrect") && (
                    <p className="auth-instruction-text">❌ Incorrect username or password - Please try again</p>
                )}

                {!isRegistration && loginMessage.toLowerCase().includes("too many") && (
                    <p className="auth-instruction-text">❌ {loginMessage}</p>
                )}
                
                {isRegistration && (
                    <>
                        <p className="auth-instruction-text">Email requirements</p>
                        <p className="sign-up-checklist-item">
                        Valid email address format: {emailValid ? "✅" : "❌"}
                        </p>

                        <p className="auth-instruction-text">Password requirements</p>
                        <p className="sign-up-checklist-item">
                        Lowercase Letter: {passwordValidation.hasLowerCase ? "✅" : "❌"}
                        </p>
                        <p className="sign-up-checklist-item">
                        Uppercase Letter: {passwordValidation.hasUpperCase ? "✅" : "❌"}
                        </p>
                        <p className="sign-up-checklist-item">
                        Number: {passwordValidation.hasNumber ? "✅" : "❌"}
                        </p>
                        <p className="sign-up-checklist-item">
                        8+ characters: {passwordValidation.hasEightCharacters ? "✅" : "❌"}
                        </p>
                        <p className="sign-up-checklist-item">
                        Special character: {passwordValidation.hasSpecialCharacters ? "✅" : "❌"}
                        </p>
                    </>
                )}

                {isRegistration && (
                confirmPassword
                    ? <p className="sign-up-checklist-item"> Password and Confirm Password Match{password !== confirmPassword ? "❌" : "✅"}</p>
                    : <p className="sign-up-checklist-item">Please retype your password to confirm</p>
                )}
                {/* {isRegistration&&signUpMessage.toLowerCase().includes("already") && (
                    

                )} */}

            
                <input className="user-input" value={email} onChange={(e)=>{setEmail(e.target.value)}} placeholder="Email" />
                <div className='password-div' >
                    <input className="user-input" value={password} onChange={handlePasswordChange} placeholder="Password" type={showPassword? "text":"password"} /> 
                    <span className="password-toggle" onClick={()=>{setShowPassword(!showPassword)}}>{showPassword ? <EyeOutlined/>:<EyeInvisibleOutlined/>}</span>
                </div>

                {isRegistration&&(

                    <div className='password-div'>
                        <input className="user-input" value={confirmPassword} onChange={(e)=>{setConfirmPassword(e.target.value)}} placeholder="Confirm Password" type={showConfirmPassword? "text":"password"} />
                        <span className="password-toggle" onClick={()=>{setShowConfirmPassword(!showConfirmPassword)}}>{showConfirmPassword ? <EyeOutlined/>:<EyeInvisibleOutlined/>}</span>
                    </div>
                    
                    
                    
            
            
            
            
            )}
                
                {isRegistration&&<select className="user-input" value={userType}onChange={(e) => setUserType(e.target.value)} required>
                    <option className="user-input" value="" disabled>Please select</option>
                    <option className="user-input" value="trainee">Trainee</option>
                    <option className="user-input" value="trainer">Trainer</option>
                </select>}
                {isAuthenticating ? (
                                    <button onClick={handleAuthenticate}><p>Authenticating...</p></button>
                                    ) : isRegistration ? (
                                    <button className="authenticate-button" onClick={handleAuthenticate} disabled={isAuthenticating||!emailValid||!passwordValid||!userType}><p>Sign up</p></button>
                                    ) : (
                                         <button className="authenticate-button" onClick={handleAuthenticate} disabled={isAuthenticating||password.length<1||!emailValid}><p>Login</p></button>
                                    )}
                {!isRegistration && (
                    <a href="/forgot-password" style={{fontSize: "1.1rem", color:"#f5c97d"}}>Forgot password?</a>
                )}
                <hr />
            <div className="register-content">
                <p>{ isRegistration ? 'Already have an account?' : 'Don\'t have an account?' }</p>
                {isRegistration ? (
                                     <button className="authenticate-button" onClick={() => setIsRegistration(false)} disabled={isAuthenticating}><p>Login</p></button>
                                        ) : (
                                        <button className="authenticate-button" onClick={() => setIsRegistration(true)} disabled={isAuthenticating}><p>Sign up</p></button>
                                        )}
                

            </div>       
        </>
    )
}