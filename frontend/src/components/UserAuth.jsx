import {useState} from 'react'
import { useAuth } from '../context/AuthContext'
import '../fanta.css'


export default function Authentication (props) {
    const {handleCloseModal,className} = props
    const [isRegistration,setIsRegistration] = useState(false)
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [confirmPassword, setConfirmPassword] = useState("")
     const [userType, setUserType] = useState("")
    const [isAuthenticating, setIsAuthenticating] = useState(false)
    const [error,setError] = useState(null)
    const [loginMessage,setLoginMessage] = useState("")
    const [signUpMessage,setSignUpMessage] = useState("")

    // Track conditions for password
    const [passwordValidation, setPasswordValidation] = useState({
        hasLowerCase: false,
        hasUpperCase: false,
        hasNumber: false,
        hasSpecialCharacters: false,
    });
    //Password check 
    const hasLowerCase = (str) => /[a-z]/.test(str);
    const hasUpperCase = (str) => /[A-Z]/.test(str);
    const hasNumber = (str) => /\d/.test(str);
    const hasSpecialCharacters = (str) => /[-+_!@#$%^&*.,?]/.test(str);




    const handlePasswordChange = (e) => {
    const value = e.target.value;
    setPassword(value)
    setPasswordValidation({
        hasLowerCase: hasLowerCase(value),
        hasUpperCase: hasUpperCase(value),
        hasNumber: hasNumber(value),
        hasSpecialCharacters: hasSpecialCharacters(value),
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
        // setSignUpMessage(defaultValue)
        
        
        setPasswordValidation({
        hasLowerCase: hasLowerCase(defaultValue),
        hasUpperCase: hasUpperCase(defaultValue),
        hasNumber: hasNumber(defaultValue),
        hasSpecialCharacters: hasSpecialCharacters(defaultValue),
        });


    };


    


    
    //accessing signup and login actions from authcontext 
    const {signUp, login} = useAuth()

    async function handleAuthenticate () {
        //if email empty/invalid, password empty/invalid or less than 6 characters, block it 
        if(!email || !email.includes("@") || !password ||password.length < 8 || isAuthenticating) {
            return }
        
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
                    resetUserAuthFields()

                }
                // if email already in use
                else if(signUpResponse.status === 409||signUpResponse.message.toLowerCase().includes("already")){

                    setSignUpMessage("This email already has an account associated with it. Please log in. If you have forgotten your password, you can reset it.")
                    alert(`❌ The email address ${email} is already in use. Please sign in, or create an account with a different email address`)
                    resetUserAuthFields()

                }


            }
            else{
                //login user
                const loginResponse = await login(email,password)
    
                

                if(loginResponse.status === 200|| loginResponse.message.toLowerCase().includes("success") ){
                    //reset the inputs and close the modal once the user is logged in
                     
                    handleCloseModal()
                    resetUserAuthFields()
                               

                }

                else if (loginResponse.status === 401 || loginResponse.message.toLowerCase().includes("incorrect")){

                    setLoginMessage("Incorrect email or password")


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
                <p>{ isRegistration ? 'Create your account' : 'Sign into your account'}</p>
                {loginMessage.toLowerCase().includes("incorrect") && (
                    <p>❌ Incorrect username or password - Please try again</p>
                )}
                
                {isRegistration&&<p>Valid email address format: {emailValid ? "✅" : "❌"}</p>}
                {isRegistration&&<p>Password has lowercase: {passwordValidation.hasLowerCase ? "✅" : "❌"}</p>}
                {isRegistration&&<p>Password has uppercase: {passwordValidation.hasUpperCase ? "✅" : "❌"}</p>}
                {isRegistration&&<p>Password has number: {passwordValidation.hasNumber ? "✅" : "❌"}</p>}
                {isRegistration&&<p>Password has special characters: {passwordValidation.hasSpecialCharacters ? "✅" : "❌"}</p>}
                {isRegistration && (
                confirmPassword
                    ? <p> Password and Confirm Password Match{password !== confirmPassword ? "❌" : "✅"}</p>
                    : <p>Please retype your password to confirm</p>
                )}
                {/* {isRegistration&&signUpMessage.toLowerCase().includes("already") && (
                    

                )} */}

            
                <input value={email} onChange={(e)=>{setEmail(e.target.value)}} placeholder="Email" />
                <input value={password} onChange={handlePasswordChange} placeholder="Password" type="password" />
                {isRegistration&&<input value={confirmPassword} onChange={(e)=>{setConfirmPassword(e.target.value)}} placeholder="Confirm Password" type="password" />}
                
                {isRegistration&&<select value={userType}onChange={(e) => setUserType(e.target.value)} required>
                    <option value="" disabled>Please select</option>
                    <option value="trainee">Trainee</option>
                    <option value="trainer">Trainer</option>
                </select>}
                {isAuthenticating ? (
                                    <button onClick={handleAuthenticate}><p>Authenticating...</p></button>
                                    ) : isRegistration ? (
                                    <button onClick={handleAuthenticate} disabled={isAuthenticating||!emailValid||!passwordValid||!userType}><p>Sign up</p></button>
                                    ) : (
                                         <button onClick={handleAuthenticate} disabled={isAuthenticating}><p>Login</p></button>
                                    )}
                <hr />
            <div className="register-content">
                <p>{ isRegistration ? 'Already have an account?' : 'Don\'t have an account?' }</p>
                {isRegistration ? (
                                     <button onClick={() => setIsRegistration(false)} disabled={isAuthenticating}><p>Login</p></button>
                                        ) : 
                                        (
                                        <button onClick={() => setIsRegistration(true)} disabled={isAuthenticating}><p>Sign up</p></button>
                                        )}
                

            </div>       
        </>
    )
}