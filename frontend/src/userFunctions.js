
export async function signUp(email,password,userType,confirmPassword) {

    const response = await fetch(`http://localhost:8000/add_user`,{
        method: 'POST',
        headers: {
            "Content-Type":"application/json"
        },
        body: JSON.stringify({
            
            email:email,
            password:password,
            user_type:userType,
            confirm_password:confirmPassword})

        })

        const data = await response.json()

        return data.message
}



export async function  login(email,password) {

    const response = await fetch(`http://localhost:8000/authenticate_user`,{
        method: 'POST',
        body: JSON.stringify({
            email:email,
            password:password

        })
    })

    const data = await response.json()
    return data.message

    
}