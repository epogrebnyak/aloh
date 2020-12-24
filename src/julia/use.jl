using JuMP
using GLPK

function calculate(purchases, max_day_storage, capacity)
    n = length(purchases)
    model = Model(GLPK.Optimizer)
    
    # definition of the production
    @variable(model, 0 <= x[1:n] <= capacity, Int)
    
    # intermidiate auxiliary variables
    cp = cumsum(purchases)
    cx = cumsum(x)

    # Inventory
    s = cx .- cp

    # Constraint 1: no inventory should left on the last day
    @constraint(model, s[n] == 0)

    # Constraint 2: inventory is defined as all non consumed production
    @constraint(model, s .>= 0)

    # Constraint 3: no inventory should be spoiled, which means that inventory should not exceed demand of the next few days
    #@constraint(model, [i = 1:n - max_day_storage + 1], cp[i + max_day_storage - 1] - cp[i] >= s[i])

    # Objective function
    @objective(model, Min, sum(s))

    optimize!(model)

    if termination_status(model) == MOI.OPTIMAL
        return (; production = Int.(value.(x)), storage = Int.(value.(s)), solved = true)
    else
        return (; production = Int[], storage = Int[], solved = false)
    end
end

production, storage, solved = calculate([0, 0, 0, 20, 0, 0, 0], 3, 5)
@assert !solved

production, storage, solved = calculate([0, 0, 15, 0, 0, 0, 0], 3, 5)
@assert solved
@assert production == [5, 5, 5, 0, 0, 0, 0]

production, storage, solved = calculate([1, 2, 5, 2, 1, 5, 3], 3, 5)
@assert solved
@assert production == [1, 2, 5, 2, 1, 5, 3]
@assert storage == [0, 0, 0, 0, 0, 0, 0]

production, storage, solved = calculate([0, 0, 2, 8, 1, 0, 1], 3, 5)
@assert solved
@assert production == [0, 0, 5, 5, 1, 0, 1]